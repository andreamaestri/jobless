document.addEventListener('alpine:init', () => {
    Alpine.store('toastManager', {
        toasts: [],
        position: 'top-right',
        expanded: false,
        layout: 'default',

        init() {
            this.watchToasts();
        },

        watchToasts() {
            this.$watch('toasts', () => {
                this.stackToasts();
            });
        },

        show(message, options = {}) {
            const toast = {
                id: 'toast-' + Math.random().toString(16).slice(2),
                message,
                type: options.type || 'default',
                description: options.description || '',
                position: options.position || this.position,
                html: options.html || '',
                autoClose: options.autoClose !== false,
                progress: 100
            };

            this.toasts.unshift(toast);

            if (toast.autoClose) {
                setTimeout(() => {
                    this.remove(toast.id);
                }, 5000);
            }
        },

        remove(id) {
            const index = this.toasts.findIndex(t => t.id === id);
            if (index > -1) {
                const toast = document.getElementById(id);
                if (toast) {
                    toast.classList.add('opacity-0');
                    toast.classList.remove('translate-y-0');
                    toast.classList.add(this.position.includes('bottom') ? 'translate-y-full' : '-translate-y-full');
                    
                    setTimeout(() => {
                        this.toasts = this.toasts.filter(t => t.id !== id);
                    }, 300);
                }
            }
        },

        stackToasts() {
            if (!this.toasts.length) return;
            
            requestAnimationFrame(() => {
                this.toasts.forEach((toast, index) => {
                    const el = document.getElementById(toast.id);
                    if (!el) return;

                    el.style.zIndex = 100 - index;
                    
                    if (this.expanded) {
                        const offset = index * (el.offsetHeight + 15);
                        if (this.position.includes('bottom')) {
                            el.style.bottom = offset + 'px';
                        } else {
                            el.style.top = offset + 'px';
                        }
                        el.style.transform = 'translateY(0) scale(1)';
                    } else {
                        if (index === 0) {
                            el.style.transform = 'translateY(0) scale(1)';
                        } else {
                            const translateY = this.position.includes('bottom') ? 
                                `-${16 * index}px` : 
                                `${16 * index}px`;
                            const scale = 1 - (index * 0.06);
                            el.style.transform = `translateY(${translateY}) scale(${scale})`;
                        }
                    }
                });
            });
        }
    });
});
