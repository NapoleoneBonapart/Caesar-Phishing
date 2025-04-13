// Initialize Socket.IO
const socket = io();

// Notification container
let notificationsContainer;

// Initialize notifications system
function initNotifications() {
    // Create notifications container if it doesn't exist
    if (!document.querySelector('.notifications-container')) {
        notificationsContainer = document.createElement('div');
        notificationsContainer.className = 'notifications-container';
        document.body.appendChild(notificationsContainer);
    } else {
        notificationsContainer = document.querySelector('.notifications-container');
    }

    // Listen for new captures
    socket.on('new_capture', (data) => {
        const pageType = data.page_type ? data.page_type.charAt(0).toUpperCase() + data.page_type.slice(1) : 'Unknown';
        const username = data.username || 'unknown user';
        
        showNotification({
            title: `New ${pageType} Capture!`,
            message: `Credentials captured from ${username}`,
            type: 'success',
            icon: 'trophy'
        });
        
        // Update counts if on main page
        if (typeof updateCounts === 'function') {
            updateCounts();
        }
        
        // Play notification sound
        playNotificationSound();
    });
}

// Show notification
function showNotification({ title, message, type = 'info', icon = 'info-circle', duration = 5000 }) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    // Create notification content
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="fas fa-${icon}"></i>
        </div>
        <div class="notification-content">
            <h6 class="notification-title">${title}</h6>
            <p class="notification-message">${message}</p>
        </div>
        <button class="notification-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add to container
    notificationsContainer.appendChild(notification);
    
    // Show notification with animation
    setTimeout(() => {
        notification.classList.add('show');
        notification.classList.add('shake');
    }, 100);
    
    // Add close button handler
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        removeNotification(notification);
    });
    
    // Auto remove after duration
    setTimeout(() => {
        removeNotification(notification);
    }, duration);
}

// Remove notification with animation
function removeNotification(notification) {
    notification.classList.remove('show');
    setTimeout(() => {
        notification.remove();
    }, 500);
}

// Play notification sound
function playNotificationSound() {
    const audio = new Audio('/static/sounds/notification.mp3');
    audio.volume = 0.5;
    audio.play().catch(e => console.log('Error playing sound:', e));
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initNotifications); 