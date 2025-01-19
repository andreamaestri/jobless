document.addEventListener('alpine:init', () => {
    Alpine.store('toastManager', {
        toasts: [],
        position: 'bottom-right',
        
        init() {
            this.toasts = [];
        },
        
        show(message, type = 'info', duration = 3000) {
            const id = Date.now();
            const toast = { id, message, type };
            
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
});
