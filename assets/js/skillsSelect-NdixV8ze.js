document.addEventListener(`alpine:init`,()=>{if(!window.Alpine){console.error(`Alpine.js not loaded`);return}let e=e=>{let t=document.getElementById(`skills-display`);if(t.querySelector(`.empty-state`),e.length===0){t.innerHTML=`
                <div class="empty-state text-base-content/50 flex items-center justify-center w-full h-full">
                    Click 'Manage Skills' to add required skills
                </div>`;return}t.innerHTML=e.map(e=>`
            <div class="badge badge-lg gap-2 badge-primary">
                <iconify-icon icon="${e.icon_dark||e.icon}" class="text-lg"></iconify-icon>
                <span>${e.name}</span>
            </div>
        `).join(``)};document.addEventListener(`skills-updated`,t=>{let n=t.detail,r=document.getElementById(`skills-input`);r&&(r.value=JSON.stringify(n));let i=document.getElementById(`skills-count`);i&&(i.textContent=`${n.length} selected`),e(n)});let t=new Map,n=(e,n)=>{let r=`heroicons:squares-2x2`;if(n&&window.ICON_NAME_MAPPING&&window.ICON_NAME_MAPPING[n]&&(e=window.ICON_NAME_MAPPING[n]),!e)return r;if(t.has(e))return t.get(e);if(t.set(e,r),window.Iconify)try{window.Iconify.iconExists(e)?t.set(e,e):window.Iconify.loadIcon(e)}catch(t){console.warn(`Error checking icon existence: ${e}`,t)}return t.get(e)};(()=>{if(window.ICON_NAME_MAPPING){let e=new Set(Object.values(window.ICON_NAME_MAPPING));if(window.Iconify){window.Iconify.loadIcons([...e]);let t=setInterval(()=>{[...e].every(e=>window.Iconify.iconExists(e))&&(clearInterval(t),i&&i.refreshOptions())},100);setTimeout(()=>clearInterval(t),5e3)}}})();let r=document.getElementById(`skills-select`);if(!r)return;let i=new TomSelect(r,{valueField:`name`,labelField:`name`,searchField:[`name`],plugins:[`remove_button`],maxItems:10,persist:!1,createFilter:null,preload:!0,onFocus:function(){let e=document.querySelector(`#id_title`);return e&&!e.value?(e.focus(),this.blur(),!1):!0},dropdownParent:`body`,maxOptions:200,hideSelected:!0,closeAfterSelect:!1,openOnFocus:!0,searchConjunction:`and`,sortField:[{field:`letter`},{field:`name`}],render:{option:function(e,t){return`<div class="flex items-center gap-4 p-2 transition-all hover:pl-4">
                    <div class="w-8 h-8 flex items-center justify-center bg-base-200 rounded-lg">
                        <iconify-icon icon="${t(n(e.icon_dark||e.icon,e.name))}" 
                                     class="text-xl text-base-content/70"
                                     onload="this.classList.add('is-loaded')"
                                     onerror="this.setAttribute('icon', 'heroicons:squares-2x2')"></iconify-icon>
                    </div>
                    <span class="font-medium">${t(e.name)}</span>
                </div>`},item:function(e,t){return`<div class="flex items-center gap-2 bg-primary/10 text-primary rounded-lg px-3 py-1.5">
                    <iconify-icon icon="${t(n(e.icon_dark||e.icon,e.name))}" 
                                 class="text-lg"
                                 onload="this.classList.add('is-loaded')"
                                 onerror="this.setAttribute('icon', 'heroicons:squares-2x2')"></iconify-icon>
                    <span>${t(e.name)}</span>
                </div>`},optgroup_header:function(e,t){return`<div class="sticky top-0 z-10 px-3 py-2 text-lg font-bold text-primary bg-base-100/95 backdrop-blur-sm">
                    ${t(e.label)}
                </div>`},no_results:function(e,t){return`<div class="p-4 text-center text-base-content/70">
                    No skills found for "${t(e.input)}"
                </div>`},loading:function(){return`<div class="p-4 text-center">
                    <span class="loading loading-spinner loading-sm"></span>
                </div>`},dropdown:function(){return`<div class="ts-dropdown">
                    <div class="ts-dropdown-content"></div>
                    <div class="p-2 border-t border-base-200">
                        <button type="button" 
                                class="btn btn-ghost btn-sm w-full gap-2"
                                onclick="window.dispatchEvent(new CustomEvent('open-skills-modal', {
                                    detail: { 
                                        selectedSkills: window.skillSelect.items.map(name => ({
                                            name: name,
                                            ...window.skillSelect.options[name]
                                        }))
                                    }
                                }))">
                            <iconify-icon icon="heroicons:squares-plus"></iconify-icon>
                            Manage Skills
                        </button>
                    </div>
                </div>`}},load:function(e,t){let r=new URL(`/jobs/skills/autocomplete/`,window.location.origin);r.searchParams.set(`q`,e||``),r.searchParams.set(`all`,`true`),fetch(r).then(e=>e.ok?e.json():Promise.reject(e)).then(e=>{if(this.clearOptions(),!e.results||!Array.isArray(e.results))throw Error(`Invalid response format`);let r=e.results.map(e=>({value:e.letter,label:e.letter,$order:e.letter.charCodeAt(0)}));t(e.results.flatMap(e=>e.skills.map(t=>({...t,letter:e.letter,icon:n(t.icon_dark||t.icon,t.name)}))),r)}).catch(e=>{console.error(`Error loading skills:`,e),Alpine&&Alpine.store(`toastManager`)&&Alpine.store(`toastManager`).show(`Failed to load skills. Please try again.`,`error`),t()})},onChange:function(e){let t=this.items.map(e=>{let t=this.options[e];return{name:t.name,icon:t.icon,icon_dark:t.icon_dark}}),n=document.getElementById(`skills-input`);n&&(n.value=JSON.stringify(t));let r=document.getElementById(`skills-count`);r&&(r.textContent=`${t.length} selected`)}});window.skillSelect=i,i.load(``),i.on(`dropdown_open`,function(e){if(e){let t=e.getBoundingClientRect(),n=Math.max(document.documentElement.clientHeight,window.innerHeight);t.bottom>n&&(e.style.top=`${n-t.height-20}px`)}}),i.on(`item_add`,function(e,t){t.classList.add(`animate-scale-in`);let n=document.getElementById(`job-form`);n&&n.classList.add(`has-skills`)}),i.on(`item_remove`,function(e){let t=document.getElementById(`job-form`);t&&i.items.length===0&&t.classList.remove(`has-skills`)}),i.on(`clear`,function(){let e=document.getElementById(`job-form`);e&&e.classList.remove(`has-skills`)}),i.on(`type`,function(e){let t=r.closest(`.ts-wrapper`);t&&t.classList.toggle(`is-searching`,e.length>0)}),document.removeEventListener(`skills-updated`,window.skillsUpdateHandler),window.skillsUpdateHandler=function(e){let t=e.detail;i.clear(!0),i.clearOptions(),t.forEach(e=>{i.addOption({name:e.name,icon:e.icon,icon_dark:e.icon_dark,letter:e.name[0].toUpperCase()}),i.addItem(e.name)});let n=document.getElementById(`skills-input`);n&&(n.value=JSON.stringify(t)),i.trigger(`change`)},document.addEventListener(`skills-updated`,window.skillsUpdateHandler)});