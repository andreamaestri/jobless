import { animate } from 'motion';

const activeAnimations = new WeakMap();
const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

export function animateElement(element, keyframes, options = {}) {
    if (!element) return;

    activeAnimations.get(element)?.stop();

    const motionOptions = reducedMotionQuery.matches
        ? { ...options, duration: 0 }
        : options;
    const controls = animate(element, keyframes, motionOptions);

    activeAnimations.set(element, controls);
    return controls;
}

export function registerMotion(Alpine, animations) {
    Alpine.magic('motion', () => ({
        animate: animateElement,
        applyAnimation(element, animationName, variant) {
            const animation = animations[animationName]?.[variant];
            if (!animation) {
                console.warn(`Animation ${animationName}.${variant} not found`);
                return;
            }

            return animateElement(element, animation.keyframes, animation.options);
        }
    }));
}
