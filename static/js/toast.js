// Toast notification system
const ToastSystem = {
    container: null,
    
    init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'fixed top-4 right-4 z-[9999] flex flex-col gap-2';
            document.body.appendChild(this.container);

            // Add styles if they don't exist
            if (!document.getElementById('toast-styles')) {
                const style = document.createElement('style');
                style.id = 'toast-styles';
                style.textContent = `
                    @keyframes slideIn {
                        from { transform: translateX(100%); opacity: 0; }
                        to { transform: translateX(0); opacity: 1; }
                    }
                    @keyframes slideOut {
                        from { transform: translateX(0); opacity: 1; }
                        to { transform: translateX(100%); opacity: 0; }
                    }
                    .toast-enter {
                        animation: slideIn 0.3s ease-out forwards;
                    }
                    .toast-exit {
                        animation: slideOut 0.3s ease-out forwards;
                    }
                `;
                document.head.appendChild(style);
            }
        }
    },

    show(message, type = 'info') {
        this.init();
        
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} shadow-lg w-80 toast-enter`;
        toast.innerHTML = `
            <div class="flex justify-between items-center w-full">
                <span class="text-sm">${message}</span>
                <button class="btn btn-ghost btn-xs btn-circle">
                    <iconify-icon icon="octicon:x-16"></iconify-icon>
                </button>
            </div>
        `;

        this.container.appendChild(toast);

        const closeBtn = toast.querySelector('button');
        closeBtn.addEventListener('click', () => this.remove(toast));

        setTimeout(() => this.remove(toast), 5000);

        return new Promise(resolve => {
            toast.addEventListener('animationend', () => {
                if (toast.classList.contains('toast-exit')) {
                    toast.remove();
                    resolve();
                }
            });
        });
    },

    remove(toast) {
        if (document.body.contains(toast)) {
            toast.classList.remove('toast-enter');
            toast.classList.add('toast-exit');
        }
    }
};

// Export for global use
window.ToastSystem = ToastSystem;
