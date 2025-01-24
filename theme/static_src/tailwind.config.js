/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */
const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
    content: [
        /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */

        /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
        '../templates/**/*.html',

        /*
         * Main templates directory of the project (BASE_DIR/templates).
         * Adjust the following line to match your project structure.
         */
        '../../templates/**/*.html',

        /*
         * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
         * Adjust the following line to match your project structure.
         */
        '../../**/templates/**/*.html',

        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your project structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the project. */
        // '../../**/*.js',

        /**
         * Python: If you use Tailwind CSS classes in Python, uncomment the following line
         * and make sure the pattern below matches your project structure.
         */
        // '../../**/*.py'
    ],
    theme: {
        extend: {
            fontFamily: {
                'sans': ['Work Sans Variable', ...defaultTheme.fontFamily.sans],
            },
        },
    },
    daisyui: {
        themes: [
          {
            Jobless: {
              'primary': '#f97316',           // Vibrant orange
              'primary-focus': '#ea580c',     // Rich orange focus
              'primary-content': '#ffffff',    // White text

              'secondary': '#c4d6ed',         // Modern indigo
              'secondary-focus': '#b6c6e2',   // Deep indigo focus
              'secondary-content': '#0c1827',  // Black text

              'accent': '#16a085',           // Keeping the teal you like
              'accent-focus': '#0d9488',     // Slightly adjusted focus
              'accent-content': '#ffffff',    // White text

              'neutral': '#334155',          // Modern slate
              'neutral-focus': '#1e293b',    // Deep slate focus
              'neutral-content': '#f8fafc',   // Very light slate

              'base-100': '#ffffff',         // Pure white
              'base-200': '#f1f5f9',         // Cool gray
              'base-300': '#e2e8f0',         // Slate gray
              'base-content': '#0f172a',     // Deep slate text

              'info': '#3b82f6',    // Bright blue for information
              'success': '#22c55e',  // Green for success
              'warning': '#f59e0b',  // Amber for warnings
              'error': '#ef4444',    // Red for errors

              '--rounded-box': '1rem',
              '--rounded-btn': '.5rem',
              '--rounded-badge': '1.9rem',

              '--animation-btn': '.25s',
              '--animation-input': '.2s',

              '--btn-text-case': 'uppercase',
              '--navbar-padding': '.5rem',
              '--border-btn': '1px',
            },
            Dark: {
              'primary': '#f97316',           // Vibrant orange
              'primary-focus': '#ea580c',     // Rich orange focus
              'primary-content': '#ffffff',    // White text

              'secondary': '#818cf8',         // Lighter indigo for dark theme
              'secondary-focus': '#6366f1',   // Indigo focus
              'secondary-content': '#ffffff',  // White text

              'accent': '#16a085',           // Keeping the teal you like
              'accent-focus': '#0d9488',     // Slightly adjusted focus
              'accent-content': '#ffffff',    // White text

              'neutral': '#1e293b',          // Deep slate
              'neutral-focus': '#0f172a',    // Darker slate focus
              'neutral-content': '#f8fafc',   // Very light slate

              'base-100': '#0f172a',         // Rich dark background
              'base-200': '#1e293b',         // Slate
              'base-300': '#334155',         // Light slate
              'base-content': '#f8fafc',     // Very light slate text

              'info': '#60a5fa',     // Lighter blue for dark theme
              'success': '#4ade80',   // Lighter green for dark theme
              'warning': '#fbbf24',   // Lighter amber for dark theme
              'error': '#f87171',     // Lighter red for dark theme

              '--rounded-box': '1rem',
              '--rounded-btn': '.5rem',
              '--rounded-badge': '1.9rem',

              '--animation-btn': '.25s',
              '--animation-input': '.2s',

              '--btn-text-case': 'uppercase',
              '--navbar-padding': '.5rem',
              '--border-btn': '1px',
            }
          },
          "lofi",
          "pastel"
        ],
    },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('daisyui'),
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}
