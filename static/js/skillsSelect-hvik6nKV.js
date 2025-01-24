document.addEventListener("alpine:init",()=>{if(!window.Alpine){console.error("Alpine.js not loaded");return}const m=e=>{const t=document.getElementById("skills-display");if(t.querySelector(".empty-state"),e.length===0){t.innerHTML=`
                <div class="empty-state text-base-content/50 flex items-center justify-center w-full h-full">
                    Click 'Manage Skills' to add required skills
                </div>`;return}t.innerHTML=e.map(n=>`
            <div class="badge badge-lg gap-2 badge-primary">
                <iconify-icon icon="${n.icon_dark||n.icon}" class="text-lg"></iconify-icon>
                <span>${n.name}</span>
            </div>
        `).join("")};document.addEventListener("skills-updated",e=>{const t=e.detail,n=document.getElementById("skills-input");n&&(n.value=JSON.stringify(t));const i=document.getElementById("skills-count");i&&(i.textContent=`${t.length} selected`),m(t)});const l=new Map,r=(e,t)=>{const n="heroicons:squares-2x2";if(t&&window.ICON_NAME_MAPPING&&window.ICON_NAME_MAPPING[t]&&(e=window.ICON_NAME_MAPPING[t]),!e)return n;if(l.has(e))return l.get(e);if(l.set(e,n),window.Iconify)try{window.Iconify.iconExists(e)?l.set(e,e):window.Iconify.loadIcon(e)}catch(i){console.warn(`Error checking icon existence: ${e}`,i)}return l.get(e)};(()=>{if(window.ICON_NAME_MAPPING){const e=new Set(Object.values(window.ICON_NAME_MAPPING));if(window.Iconify){window.Iconify.loadIcons([...e]);const t=setInterval(()=>{[...e].every(i=>window.Iconify.iconExists(i))&&(clearInterval(t),o&&o.refreshOptions())},100);setTimeout(()=>clearInterval(t),5e3)}}})();const d=document.getElementById("skills-select");if(!d)return;const o=new TomSelect(d,{valueField:"name",labelField:"name",searchField:["name"],plugins:["remove_button"],maxItems:10,persist:!1,createFilter:null,preload:!0,onFocus:function(){const e=document.querySelector("#id_title");return e&&!e.value?(e.focus(),this.blur(),!1):!0},dropdownParent:"body",maxOptions:200,hideSelected:!0,closeAfterSelect:!1,openOnFocus:!0,searchConjunction:"and",sortField:[{field:"letter"},{field:"name"}],render:{option:function(e,t){const n=r(e.icon_dark||e.icon,e.name);return`<div class="flex items-center gap-4 p-2 transition-all hover:pl-4">
                    <div class="w-8 h-8 flex items-center justify-center bg-base-200 rounded-lg">
                        <iconify-icon icon="${t(n)}" 
                                     class="text-xl text-base-content/70"
                                     onload="this.classList.add('is-loaded')"
                                     onerror="this.setAttribute('icon', 'heroicons:squares-2x2')"></iconify-icon>
                    </div>
                    <span class="font-medium">${t(e.name)}</span>
                </div>`},item:function(e,t){const n=r(e.icon_dark||e.icon,e.name);return`<div class="flex items-center gap-2 bg-primary/10 text-primary rounded-lg px-3 py-1.5">
                    <iconify-icon icon="${t(n)}" 
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
                </div>`}},load:function(e,t){const n=new URL("/jobs/skills/autocomplete/",window.location.origin);n.searchParams.set("q",e||""),n.searchParams.set("all","true"),fetch(n).then(i=>i.ok?i.json():Promise.reject(i)).then(i=>{if(this.clearOptions(),!i.results||!Array.isArray(i.results))throw new Error("Invalid response format");const u=i.results.map(s=>({value:s.letter,label:s.letter,$order:s.letter.charCodeAt(0)})),c=i.results.flatMap(s=>s.skills.map(a=>({...a,letter:s.letter,icon:r(a.icon_dark||a.icon,a.name)})));t(c,u)}).catch(i=>{console.error("Error loading skills:",i),Alpine&&Alpine.store("toastManager")&&Alpine.store("toastManager").show("Failed to load skills. Please try again.","error"),t()})},onChange:function(e){const t=this.items.map(u=>{const c=this.options[u];return{name:c.name,icon:c.icon,icon_dark:c.icon_dark}}),n=document.getElementById("skills-input");n&&(n.value=JSON.stringify(t));const i=document.getElementById("skills-count");i&&(i.textContent=`${t.length} selected`)}});window.skillSelect=o,o.load(""),o.on("dropdown_open",function(e){if(e){const t=e.getBoundingClientRect(),n=Math.max(document.documentElement.clientHeight,window.innerHeight);t.bottom>n&&(e.style.top=`${n-t.height-20}px`)}}),o.on("item_add",function(e,t){t.classList.add("animate-scale-in");const n=document.getElementById("job-form");n&&n.classList.add("has-skills")}),o.on("item_remove",function(e){const t=document.getElementById("job-form");t&&o.items.length===0&&t.classList.remove("has-skills")}),o.on("clear",function(){const e=document.getElementById("job-form");e&&e.classList.remove("has-skills")}),o.on("type",function(e){const t=d.closest(".ts-wrapper");t&&t.classList.toggle("is-searching",e.length>0)}),document.removeEventListener("skills-updated",window.skillsUpdateHandler),window.skillsUpdateHandler=function(e){const t=e.detail;o.clear(!0),o.clearOptions(),t.forEach(i=>{o.addOption({name:i.name,icon:i.icon,icon_dark:i.icon_dark,letter:i.name[0].toUpperCase()}),o.addItem(i.name)});const n=document.getElementById("skills-input");n&&(n.value=JSON.stringify(t)),o.trigger("change")},document.addEventListener("skills-updated",window.skillsUpdateHandler)});
