from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from src.models import (
    db, Booking, BookingStatus, Service, Store, User, UserRole, Payment, PaymentStatus
)
from src.utils.auth import get_current_user, ensure_store_access
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics based on user role"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get date range from query params (default: last 30 days)
        days = request.args.get('days', 30, type=int)
        start_date = datetime.now() - timedelta(days=days)
        today = datetime.now().date()
        
        stats = {}
        
        if current_user.role == UserRole.CLIENT:
            # Client statistics
            stats = get_client_stats(current_user.id, start_date, today)
        elif current_user.role == UserRole.STORE_MANAGER:
            # Store manager statistics
            if not current_user.store_id:
                return jsonify({'error': 'Store not found for manager'}), 404
            stats = get_store_manager_stats(current_user.store_id, start_date, today)
        elif current_user.role == UserRole.ADMIN:
            # Admin statistics (all stores)
            stats = get_admin_stats(start_date, today)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_client_stats(user_id, start_date, today):
    """Get statistics for client users"""
    # Total bookings
    total_bookings = Booking.query.filter_by(client_user_id=user_id).count()
    
    # Upcoming bookings
    upcoming_bookings = Booking.query.filter(
        and_(
            Booking.client_user_id == user_id,
            Booking.booking_date >= today,
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING])
        )
    ).count()
    
    # Completed bookings
    completed_bookings = Booking.query.filter(
        and_(
            Booking.client_user_id == user_id,
            Booking.status == BookingStatus.COMPLETED
        )
    ).count()
    
    # Total spent
    total_spent = db.session.query(func.sum(Payment.amount)).filter(
        and_(
            Payment.user_id == user_id,
            Payment.status == PaymentStatus.SUCCEEDED
        )
    ).scalar() or 0
    
    # Recent bookings (last 5)
    recent_bookings = Booking.query.filter_by(
        client_user_id=user_id
    ).order_by(Booking.created_at.desc()).limit(5).all()
    
    recent_bookings_data = []
    for booking in recent_bookings:
        data = booking.to_dict()
        data['service'] = booking.service.to_dict() if booking.service else None
        data['store'] = booking.store.to_dict() if booking.store else None
        recent_bookings_data.append(data)
    
    return {
        'totalBookings': total_bookings,
        'upcomingBookings': upcoming_bookings,
        'completedBookings': completed_bookings,
        'totalSpent': float(total_spent),
        'recentBookings': recent_bookings_data
    }

def get_store_manager_stats(store_id, start_date, today):
    """Get statistics for store manager users"""
    # Total bookings
    total_bookings = Booking.query.filter_by(store_id=store_id).count()
    
    # Today's bookings
    today_bookings = Booking.query.filter(
        and_(
            Booking.store_id == store_id,
            Booking.booking_date == today
        )
    ).count()
    
    # This month's bookings
    first_day_of_month = today.replace(day=1)
    month_bookings = Booking.query.filter(
        and_(
            Booking.store_id == store_id,
            Booking.booking_date >= first_day_of_month
        )
    ).count()
    
    # Last month's bookings for comparison
    last_month_start = (first_day_of_month - timedelta(days=1)).replace(day=1)
    last_month_end = first_day_of_month - timedelta(days=1)
    last_month_bookings = Booking.query.filter(
        and_(
            Booking.store_id == store_id,
            Booking.booking_date >= last_month_start,
            Booking.booking_date <= last_month_end
        )
    ).count()
    
    # Calculate percentage change
    booking_change = 0
    if last_month_bookings > 0:
        booking_change = ((month_bookings - last_month_bookings) / last_month_bookings) * 100
    
    # Revenue (this month)
    month_revenue = db.session.query(func.sum(Payment.amount)).join(Booking).filter(
        and_(
            Booking.store_id == store_id,
            Booking.booking_date >= first_day_of_month,
            Payment.status == PaymentStatus.SUCCEEDED
        )
    ).scalar() or 0
    
    # Last month revenue for comparison
    last_month_revenue = db.session.query(func.sum(Payment.amount)).join(Booking).filter(
        and_(
            Booking.store_id == store_id,
            Booking.booking_date >= last_month_start,
            Booking.booking_date <= last_month_end,
            Payment.status == PaymentStatus.SUCCEEDED
        )
    ).scalar() or 0
    
    # Calculate revenue change
    revenue_change = 0
    if last_month_revenue > 0:
        revenue_change = ((month_revenue - last_month_revenue) / last_month_revenue) * 100
    
    # Total customers (unique clients)
    total_customers = db.session.query(func.count(func.distinct(Booking.client_user_id))).filter(
        Booking.store_id == store_id
    ).scalar() or 0
    
    # New customers this week
    week_start = today - timedelta(days=today.weekday())
    new_customers_week = db.session.query(func.count(func.distinct(Booking.client_user_id))).filter(
        and_(
            Booking.store_id == store_id,
            Booking.created_at >= week_start
        )
    ).scalar() or 0
    
    # Booking status breakdown for today
    today_confirmed = Booking.query.filter(
        and_(
            Booking.store_id == store_id,
            Booking.booking_date == today,
            Booking.status == BookingStatus.CONFIRMED
        )
    ).count()
    
    today_pending = Booking.query.filter(
        and_(
            Booking.store_id == store_id,
            Booking.booking_date == today,
            Booking.status == BookingStatus.PENDING
        )
    ).count()
    
    # Recent bookings (last 10)
    recent_bookings = Booking.query.filter_by(
        store_id=store_id
    ).order_by(Booking.created_at.desc()).limit(10).all()
    
    recent_bookings_data = []
    for booking in recent_bookings:
        data = booking.to_dict()
        data['service'] = booking.service.to_dict() if booking.service else None
        data['client'] = booking.client.to_dict() if booking.client else None
        recent_bookings_data.append(data)
    
    # Popular services (top 5)
    popular_services = db.session.query(
        Service.id,
        Service.name,
        func.count(Booking.id).label('booking_count')
    ).join(Booking).filter(
        Booking.store_id == store_id
    ).group_by(Service.id, Service.name).order_by(
        func.count(Booking.id).desc()
    ).limit(5).all()
    
    popular_services_data = [
        {'id': str(s.id), 'name': s.name, 'bookingCount': s.booking_count}
        for s in popular_services
    ]
    
    return {
        'totalBookings': total_bookings,
        'todayBookings': today_bookings,
        'monthBookings': month_bookings,
        'bookingChange': round(booking_change, 1),
        'revenue': float(month_revenue),
        'revenueChange': round(revenue_change, 1),
        'customers': total_customers,
        'newCustomersWeek': new_customers_week,
        'todayConfirmed': today_confirmed,
        'todayPending': today_pending,
        'recentBookings': recent_bookings_data,
        'popularServices': popular_services_data
    }

def get_admin_stats(start_date, today):
    """Get statistics for admin users (all stores)"""
    # Total stores
    total_stores = Store.query.count()
    
    # Active stores (with bookings in last 30 days)
    active_stores = db.session.query(func.count(func.distinct(Booking.store_id))).filter(
        Booking.booking_date >= start_date
    ).scalar() or 0
    
    # Total bookings
    total_bookings = Booking.query.count()
    
    # Total revenue
    total_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == PaymentStatus.SUCCEEDED
    ).scalar() or 0
    
    # Total users
    total_users = User.query.count()
    
    # Total clients
    total_clients = User.query.filter_by(role=UserRole.CLIENT).count()
    
    # Total managers
    total_managers = User.query.filter_by(role=UserRole.STORE_MANAGER).count()
    
    # Recent bookings (last 10 across all stores)
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    
    recent_bookings_data = []
    for booking in recent_bookings:
        data = booking.to_dict()
        data['service'] = booking.service.to_dict() if booking.service else None
        data['store'] = booking.store.to_dict() if booking.store else None
        data['client'] = booking.client.to_dict() if booking.client else None
        recent_bookings_data.append(data)
    
    # Top stores by revenue
    top_stores = db.session.query(
        Store.id,
        Store.name,
        func.sum(Payment.amount).label('revenue')
    ).join(Booking, Store.id == Booking.store_id).join(
        Payment, Booking.id == Payment.booking_id
    ).filter(
        Payment.status == PaymentStatus.SUCCEEDED
    ).group_by(Store.id, Store.name).order_by(
        func.sum(Payment.amount).desc()
    ).limit(5).all()
    
    top_stores_data = [
        {'id': str(s.id), 'name': s.name, 'revenue': float(s.revenue)}
        for s in top_stores
    ]
    
    return {
        'totalStores': total_stores,
        'activeStores': active_stores,
        'totalBookings': total_bookings,
        'totalRevenue': float(total_revenue),
        'totalUsers': total_users,
        'totalClients': total_clients,
        'totalManagers': total_managers,
        'recentBookings': recent_bookings_data,
        'topStores': top_stores_data
    }

@dashboard_bp.route('/dashboard/analytics/bookings', methods=['GET'])
@jwt_required()
def get_booking_analytics():
    """Get booking analytics over time"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get date range from query params
        days = request.args.get('days', 30, type=int)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Build base query based on role
        query = db.session.query(
            Booking.booking_date,
            func.count(Booking.id).label('count')
        )
        
        if current_user.role == UserRole.STORE_MANAGER:
            if not current_user.store_id:
                return jsonify({'error': 'Store not found for manager'}), 404
            query = query.filter(Booking.store_id == current_user.store_id)
        elif current_user.role == UserRole.CLIENT:
            query = query.filter(Booking.client_user_id == current_user.id)
        
        # Apply date filter and group by date
        analytics = query.filter(
            and_(
                Booking.booking_date >= start_date,
                Booking.booking_date <= end_date
            )
        ).group_by(Booking.booking_date).order_by(Booking.booking_date).all()
        
        # Format data for charts
        analytics_data = [
            {'date': str(a.booking_date), 'count': a.count}
            for a in analytics
        ]
        
        return jsonify(analytics_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/dashboard/analytics/revenue', methods=['GET'])
@jwt_required()
def get_revenue_analytics():
    """Get revenue analytics over time"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only for store managers and admins
        if current_user.role == UserRole.CLIENT:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get date range from query params
        days = request.args.get('days', 30, type=int)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Build base query
        query = db.session.query(
            Booking.booking_date,
            func.sum(Payment.amount).label('revenue')
        ).join(Payment, Booking.id == Payment.booking_id)
        
        if current_user.role == UserRole.STORE_MANAGER:
            if not current_user.store_id:
                return jsonify({'error': 'Store not found for manager'}), 404
            query = query.filter(Booking.store_id == current_user.store_id)
        
        # Apply filters
        analytics = query.filter(
            and_(
                Booking.booking_date >= start_date,
                Booking.booking_date <= end_date,
                Payment.status == PaymentStatus.SUCCEEDED
            )
        ).group_by(Booking.booking_date).order_by(Booking.booking_date).all()
        
        # Format data for charts
        analytics_data = [
            {'date': str(a.booking_date), 'revenue': float(a.revenue) if a.revenue else 0}
            for a in analytics
        ]
        
        return jsonify(analytics_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
