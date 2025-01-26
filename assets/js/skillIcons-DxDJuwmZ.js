function w(o,i){const t=()=>i();return o.addEventListener("mouseenter",t),o.addEventListener("mouseleave",i),o.addEventListener("touchstart",t,{passive:!0}),o.addEventListener("touchend",i),o.addEventListener("touchcancel",i),()=>{o.removeEventListener("mouseenter",t),o.removeEventListener("mouseleave",i),o.removeEventListener("touchstart",t),o.removeEventListener("touchend",i),o.removeEventListener("touchcancel",i)}}class d{constructor(){this.darkMode=window.matchMedia("(prefers-color-scheme: dark)").matches,this.watchThemeChanges(),this.initialized=!0,this.iconMappings={}}async initialize(){try{if(window.MODAL_ICON_MAPPING)this.iconMappings=window.MODAL_ICON_MAPPING;else{const i=await fetch("/jobs/api/skills/");if(!i.ok)throw new Error("Failed to load skills data");(await i.json()).forEach(e=>{this.iconMappings[e.name.toLowerCase()]=e.icon})}await this.updateIcons(),console.log("Icons initialized successfully")}catch(i){console.warn("Icon initialization error:",i)}}async refreshIconElement(i,t){var e,r;if(!(!i||!t))try{i.style.display="inline-block",i.style.visibility="visible";const n=t.toLowerCase(),s=this.iconMappings[n]||((e=window.MODAL_ICON_MAPPING)==null?void 0:e[n])||"heroicons:academic-cap",h=((r=window.MODAL_DARK_VARIANTS)==null?void 0:r[s])||s;i.setAttribute("icon",this.darkMode?h:s),i.setAttribute("width","20"),i.setAttribute("height","20");const c=i.parentElement;if(c){const a=i.nextSibling;i.remove(),a?c.insertBefore(i,a):c.appendChild(i)}}catch{console.warn(`Failed to refresh icon for skill: ${t}`),i.setAttribute("icon","heroicons:academic-cap")}}watchThemeChanges(){window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change",t=>{this.darkMode=t.matches,this.updateIcons()})}async updateIcons(){var t,e,r;const i=document.querySelectorAll("iconify-icon");for(const n of i){const s=((t=n.closest("[data-tip]"))==null?void 0:t.getAttribute("data-tip"))||((r=(e=n.closest(".skill-card"))==null?void 0:e.querySelector(".skill-name"))==null?void 0:r.textContent);s&&await this.refreshIconElement(n,s)}}getIconForSkill(i){var e;const t=i.toLowerCase();return this.iconMappings[t]||((e=window.MODAL_ICON_MAPPING)==null?void 0:e[t])||"heroicons:academic-cap"}getDarkIconForSkill(i){var e;const t=this.getIconForSkill(i);return((e=window.MODAL_DARK_VARIANTS)==null?void 0:e[t])||t}}async function l(){try{window.skillIconsHelper||(window.skillIconsHelper=new d,await window.skillIconsHelper.initialize())}catch(o){console.warn("Skills initialization error:",o)}}window.skillIconsHelper=new d;l().catch(console.warn);export{d as SkillIconsHelper,w as setupHover};
