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
                    'primary': '#f97316',           // Vibrant orange
                    'primary-focus': '#ea580c',     // Deeper orange
                    'primary-content': '#ffffff',    // White text

                    'secondary': '#8b5cf6',         // Warm purple
                    'secondary-focus': '#7c3aed',   // Deeper purple
                    'secondary-content': '#ffffff',  // White text

                    'accent': '#14b8a6',           // Teal
                    'accent-focus': '#0d9488',     // Deeper teal
                    'accent-content': '#ffffff',    // White text

                    'neutral': '#1f2937',          // Cool gray
                    'neutral-focus': '#111827',    // Darker gray
                    'neutral-content': '#ffffff',   // White text

                    'base-100': '#ffffff',         // Pure white
                    'base-200': '#f3f4f6',         // Light gray
                    'base-300': '#e5e7eb',         // Slightly darker gray
                    'base-content': '#1f2937',     // Dark text

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
                    'primary': '#f97316',           // Bright orange
                    'primary-focus': '#ea580c',     // Deeper orange
                    'primary-content': '#ffffff',    // White text

                    'secondary': '#a78bfa',         // Soft purple
                    'secondary-focus': '#8b5cf6',   // Deeper purple
                    'secondary-content': '#ffffff',  // White text

                    'accent': '#2dd4bf',           // Bright teal
                    'accent-focus': '#14b8a6',     // Deeper teal
                    'accent-content': '#ffffff',    // White text

                    'neutral': '#1e293b',          // Slate
                    'neutral-focus': '#0f172a',    // Deep slate
                    'neutral-content': '#ffffff',   // White text

                    'base-100': '#0f172a',         // Deep slate
                    'base-200': '#1e293b',         // Slate
                    'base-300': '#334155',         // Light slate
                    'base-content': '#f8fafc',     // Very light slate

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
