function d(t){let s=()=>{let r,l;try{l=localStorage}catch(a){console.error(a),console.warn("Alpine: $persist is using temporary storage since localStorage is unavailable.");let e=new Map;l={getItem:e.get.bind(e),setItem:e.set.bind(e)}}return t.interceptor((a,e,i,n,p)=>{let o=r||`_x_${n}`,u=g(o,l)?f(o,l):a;return i(u),t.effect(()=>{let c=e();m(o,c,l),i(c)}),u},a=>{a.as=e=>(r=e,a),a.using=e=>(l=e,a)})};Object.defineProperty(t,"$persist",{get:()=>s()}),t.magic("persist",s),t.persist=(r,{get:l,set:a},e=localStorage)=>{let i=g(r,e)?f(r,e):l();a(i),t.effect(()=>{let n=l();m(r,n,e),a(n)})}}function g(t,s){return s.getItem(t)!==null}function f(t,s){let r=s.getItem(t,s);if(r!==void 0)return JSON.parse(r)}function m(t,s,r){r.setItem(t,JSON.stringify(s))}var S=d;export{S as m,d as s};
