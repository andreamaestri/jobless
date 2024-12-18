/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

const { default: daisyui } = require('daisyui');

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
    daisyui: {
        themes: [
            {
                'Jobless': {
                    'primary' : '#ec8751',
                    'primary-focus' : '#ca5516',
                    'primary-content' : '#f5f0eb',

                    'secondary' : '#cb581a',
                    'secondary-focus' : '#a04718',
                    'secondary-content' : '#f5f0eb',

                    'accent' : '#9c3116',
                    'accent-focus' : '#be3513',
                    'accent-content' : '#f5f0eb',

                    'neutral' : '#34322f',
                    'neutral-focus' : '#868179',
                    'neutral-content' : '#ebe7e2',

                    'base-100' : '#ebe7e2',
                    'base-200' : '#6b6761',
                    'base-300' : '#1b1a18',
                    'base-content' : '#34322f',

                    'info' : '#ec8751',
                    'success' : '#f2a982',
                    'warning' : '#b88b75',
                    'error' : '#bd6b56',

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
