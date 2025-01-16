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
                'Jobless': {
                    'primary': '#e67e22',           // Softer orange
                    'primary-focus': '#d35400',     // Deeper orange
                    'primary-content': '#ffffff',    // White text

                    'secondary': '#34495e',         // Slate blue
                    'secondary-focus': '#2c3e50',   // Deeper slate
                    'secondary-content': '#ffffff',  // White text

                    'accent': '#16a085',           // Soft teal
                    'accent-focus': '#147a6b',     // Deeper teal
                    'accent-content': '#ffffff',    // White text

                    'neutral': '#2c3e50',          // Dark slate
                    'neutral-focus': '#233140',    // Deeper slate
                    'neutral-content': '#ecf0f1',   // Light gray text

                    'base-100': '#f9fafb',         // Off white
                    'base-200': '#f1f5f9',         // Light gray
                    'base-300': '#e2e8f0',         // Medium gray
                    'base-content': '#2c3e50',     // Dark slate text

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
                'Dark': {
                    'primary': '#e67e22',           // Warm orange
                    'primary-focus': '#d35400',     // Deep orange
                    'primary-content': '#ffffff',    // White text

                    'secondary': '#34495e',         // Dark slate blue
                    'secondary-focus': '#2c3e50',   // Deeper slate
                    'secondary-content': '#ffffff',  // White text

                    'accent': '#16a085',           // Dark teal
                    'accent-focus': '#147a6b',     // Deeper teal
                    'accent-content': '#ffffff',    // White text

                    'neutral': '#2c3e50',          // Rich slate
                    'neutral-focus': '#233140',    // Deep slate
                    'neutral-content': '#ecf0f1',   // Light gray text

                    'base-100': '#1a202c',         // Dark background
                    'base-200': '#2d3748',         // Slightly lighter
                    'base-300': '#4a5568',         // Medium gray
                    'base-content': '#f7fafc',     // Light text

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
                },
            },
            "lofi",
            "pastel",
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
