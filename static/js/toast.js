document.addEventListener("alpine:init", () => {
  Alpine.store("toastManager", {
    toasts: [],

    init() {
      // Initialize toasts from Django messages if present
      const messages = this.getInitialMessages();
      messages.forEach((message, index) => {
        this.addToast({
          id: Date.now() + index,
          message: message.text,
          type: message.type,
          progress: 100
        });
      });
    },

    getInitialMessages() {
      // This would be populated by Django template context
      // The structure is handled in the template itself
      return [];
    },

    addToast(toast) {
      this.toasts.push(toast);
      
      const startTime = Date.now();
      const duration = 5000;
      
      const interval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        toast.progress = Math.max(0, 100 - (elapsed / duration * 100));
        
        if (elapsed >= duration) {
          clearInterval(interval);
          this.removeToast(toast.id);
        }
      }, 100);
    },

    removeToast(id) {
      const index = this.toasts.findIndex(t => t.id === id);
      if (index > -1) {
        this.toasts[index].removing = true;
        setTimeout(() => {
          this.toasts = this.toasts.filter(t => t.id !== id);
        }, 300);
      }
    }
  });
});

// Add CSS styles for toast animations
const style = document.createElement('style');
style.textContent = `
  .toast > * {
    animation: toast-enter 0.3s ease-out;
  }
  
  @keyframes toast-enter {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  
  .animate-leave {
    animation: toast-leave 0.3s ease-in forwards;
  }
  
  @keyframes toast-leave {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(100%);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);
