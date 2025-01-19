{
    currentPreviewLetter: null,
    lastTouchY: null,
    isScrolling: false,

    startLetterDrag(e) {
        this.lastTouchY = e.touches[0].clientY;
        this.isScrolling = false;
    },

    handleLetterDrag(e) {
        if (!this.lastTouchY) return;
        
        const touch = e.touches[0];
        const nav = e.currentTarget;
        const rect = nav.getBoundingClientRect();
        const percentage = (touch.clientY - rect.top) / rect.height;
        const index = Math.floor(percentage * nav.children.length);
        const button = nav.children[index];
        
        if (button && !this.isScrolling) {
            e.preventDefault();
            const letter = button.textContent.trim();
            this.previewLetter(letter);
            this.jumpToLetter(letter);
        }
    },

    endLetterDrag() {
        this.lastTouchY = null;
        setTimeout(() => this.hideLetterPreview(), 1000);
    },

    previewLetter(letter) {
        this.currentPreviewLetter = letter;
    },

    hideLetterPreview() {
        this.currentPreviewLetter = null;
    },

    handleScroll(e) {
        if (!this.isScrolling) {
            this.isScrolling = true;
            
            // Find which group is most visible
            const container = e.target;
            const groups = container.querySelectorAll('.skill-group');
            let mostVisible = null;
            let maxVisibleHeight = 0;
            
            groups.forEach(group => {
                const rect = group.getBoundingClientRect();
                const visibleHeight = Math.min(rect.bottom, window.innerHeight) - 
                                    Math.max(rect.top, 0);
                
                if (visibleHeight > maxVisibleHeight) {
                    maxVisibleHeight = visibleHeight;
                    mostVisible = group;
                }
            });
            
            if (mostVisible) {
                const letter = mostVisible.dataset.letter;
                this.currentLetter = letter;
                document.querySelectorAll('.skill-group').forEach(g => {
                    g.classList.toggle('active', g === mostVisible);
                });
            }
            
            setTimeout(() => this.isScrolling = false, 100);
        }
    }
}
