// ViewTransition helper for smoother page transitions
class ViewTransitionHelper {
    constructor() {
        this.setupNavigationHandler();
        this.regexPatterns = {
            title: /<title>([\s\S]*)<\/title>/i,
            scripts: /<(script|SCRIPT)[\s\S]*?<\/(script|SCRIPT)>/g,
            main: /<main[^>]*>([\s\S]*)<\/main>/i
        };
    }

    setupNavigationHandler() {
        var self = this;
        document.addEventListener('click', function(e) {
            var link = e.target.closest('a');
            if (!self.isValidNavigation(link)) return;

            e.preventDefault();
            self.handleNavigation(link.pathname, link.href);
        });

        window.addEventListener('popstate', function() {
            self.handleNavigation(window.location.pathname, window.location.href);
        });
    }

    async handleNavigation(pathname, href) {
        try {
            const response = await fetch(pathname);
            const html = await response.text();
            
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            const currentMain = document.querySelector('main');
            const newMain = doc.querySelector('main');
            
            if (currentMain && newMain) {
                // Prepare the new content but keep it hidden
                const wrapper = document.createElement('div');
                wrapper.innerHTML = newMain.innerHTML;
                wrapper.className = 'page-transition-wrapper';
                
                this.startViewTransition(() => {
                    // Animate out current content
                    currentMain.style.animation = 'page-leave 0.3s ease-out forwards';
                    
                    // After current content fades out, update content and animate in
                    setTimeout(() => {
                        currentMain.innerHTML = wrapper.innerHTML;
                        currentMain.style.animation = 'page-enter 0.3s ease-out forwards';
                        document.title = doc.title;
                        
                        // Re-initialize Alpine components
                        if (window.Alpine) {
                            document.querySelectorAll('[x-data]').forEach(el => {
                                window.Alpine.initTree(el);
                            });
                        }
                    }, 300);
                });
                
                window.history.pushState({}, '', href);
                window.scrollTo(0, 0);
            }
        } catch (error) {
            console.error('Navigation failed:', error);
            window.location.href = href;
        }
    }

    startViewTransition(callback) {
        if (!document.startViewTransition) {
            const transitions = document.querySelectorAll('.page-transition-wrapper');
            transitions.forEach(t => t.style.animation = 'none');
            
            callback();
            return;
        }

        document.documentElement.classList.add('transition-active');
        
        const transition = document.startViewTransition(() => {
            callback();
        });

        transition.finished.finally(() => {
            document.documentElement.classList.remove('transition-active');
        });

        return transition;
    }

    isValidNavigation(link) {
        return link && 
               link.href &&
               link.origin === location.origin &&
               !link.hasAttribute('download') &&
               !link.target &&
               !link.href.includes('#');
    }
}

// Initialize the handler when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    new ViewTransitionHelper();
});
