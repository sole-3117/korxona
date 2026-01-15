const api = "https://YOUR_RENDER_URL";

async function login(){
 const r=await fetch(api+"/login",{method:"POST",
 headers:{"Content-Type":"application/json"},
 body:JSON.stringify({username:u.value,password:p.value})
 });
 const d=await r.json();
 localStorage.t=d.token;
}

const h=()=>({Authorization:"Bearer "+localStorage.t,
 "Content-Type":"application/json"});

const sale=()=>fetch(api+"/sales",{method:"POST",headers:h(),
 body:JSON.stringify({total:10000})});

const ret=()=>fetch(api+"/returns",{method:"POST",headers:h(),
 body:JSON.stringify({sale_id:1,amount:5000})});

const exp=()=>fetch(api+"/expenses",{method:"POST",headers:h(),
 body:JSON.stringify({type:"ovqat",amount:3000})});

const rep=async()=>out.textContent=
 JSON.stringify(await (await fetch(api+"/reports",{headers:h()})).json(),null,2);
