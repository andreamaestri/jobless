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
            var response = await fetch(pathname);
            var html = await response.text();
            
            var parser = new DOMParser();
            var doc = parser.parseFromString(html, 'text/html');
            
            // Preserve the main element's attributes
            var currentMain = document.querySelector('main');
            var newMain = doc.querySelector('main');
            
            if (currentMain && newMain) {
                this.startViewTransition(() => {
                    // Keep Alpine.js bindings and classes
                    currentMain.innerHTML = newMain.innerHTML;
                    document.title = doc.title;
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
            callback();
            return;
        }

        document.documentElement.classList.add('transition-active');
        
        const transition = document.startViewTransition(() => {
            callback();
            
            // Re-initialize Alpine components
            if (window.Alpine) {
                document.querySelectorAll('[x-data]').forEach(el => {
                    window.Alpine.initTree(el);
                });
            }

            // Preserve sidebar state
            const sidebar = document.querySelector('aside');
            if (sidebar) {
                sidebar.style.visibility = 'visible';
                sidebar.style.opacity = '1';
            }
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
