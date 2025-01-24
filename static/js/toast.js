import Alpine from 'alpinejs'

export function initializeToastManager() {
    Alpine.store('toastManager', {
        toasts: [],
        position: 'bottom-right',
        
        init() {
            this.toasts = [];
        },
        
        show(options = {}, duration = 3000) {
            const id = Date.now();
            const toast = {
                id,
                type: options.type || 'info',
                message: options.message || '',
                description: options.description || ''
            };
            
            this.toasts.push(toast);
            
            if (duration > 0) {
                setTimeout(() => {
                    this.remove(id);
                }, duration);
            }
        },
        
        remove(id) {
            const index = this.toasts.findIndex(t => t.id === id);
            if (index > -1) {
                this.toasts.splice(index, 1);
            }
        },
        
        clear() {
            this.toasts = [];
        }
    });
}

// Initialize when Alpine loads
document.addEventListener('alpine:init', initializeToastManager);

export default {
    initializeToastManager
};
