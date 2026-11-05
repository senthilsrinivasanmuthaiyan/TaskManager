const PROJECTS = [
  {key:"clinic",name:"Clinic ERP",repo:"senthilsrinivasanmuthaiyan/clinic",mission:"Patients, appointments, clinical workflows, billing and tenant isolation."},
  {key:"school",name:"School ERP",repo:"senthilsrinivasanmuthaiyan/school",mission:"Admissions, students, parents, attendance, fees, transport and school administration."},
  {key:"jewel-pos",name:"Jewel POS ERP",repo:"senthilsrinivasanmuthaiyan/jewel-pos",mission:"Jewellery POS, metal rates, purity, tagged inventory, job work and GST workflows."},
  {key:"universal-pos",name:"Universal POS ERP",repo:"senthilsrinivasanmuthaiyan/universal-pos",mission:"Multi-industry POS, barcode, checkout, inventory, purchasing, returns and reports."},
  {key:"manufacturing",name:"Manufacturing ERP",repo:"senthilsrinivasanmuthaiyan/manufacturing",mission:"BOM, production planning, work orders, procurement, quality and traceable stock."},
  {key:"chitfund",name:"Chit Fund ERP",repo:"senthilsrinivasanmuthaiyan/chitfund",mission:"Schemes, members, collections, auctions, payouts, agent settlement and audit."},
  {key:"onepass",name:"OnePass",repo:"senthilsrinivasanmuthaiyan/onepass",mission:"Consumer marketplace, merchant portal, bookings, membership and loyalty."},
  {key:"saas-admin",name:"SaaS Admin",repo:"senthilsrinivasanmuthaiyan/sassadmin",mission:"Tenant provisioning, plans, entitlements, identity and platform operations."},
  {key:"travel",name:"Travel",repo:"senthilsrinivasanmuthaiyan1/travel",mission:"Travel marketplace, itineraries, bookings, payments and traveller experience."},
  {key:"transport-fleet",name:"Transport Fleet ERP",repo:"senthilsrinivasanmuthaiyan1/transport-fleet",mission:"Fleet, vehicles, drivers, trips, dispatch, GPS, maintenance and compliance."},
  {key:"retail",name:"Retail ERP",repo:"senthilsrinivasanmuthaiyan1/retail",mission:"Retail catalog, POS, inventory, procurement, customer app and fulfilment."}
];

const MODEL = "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b";
const COOKIE = "__Host-erp_agent_session";
const encoder = new TextEncoder();

function json(data, status=200, headers={}) {
  return new Response(JSON.stringify(data), {status,headers:{"content-type":"application/json; charset=utf-8","cache-control":"no-store",...headers}});
}
function b64url(bytes) {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/=/g,"").replace(/\+/g,"-").replace(/\//g,"_");
}
function fromB64url(value) {
  const normalized = value.replace(/-/g,"+").replace(/_/g,"/");
  const padded = normalized + "=".repeat((4-normalized.length%4)%4);
  return Uint8Array.from(atob(padded), c => c.charCodeAt(0));
}
async function sign(value, secret) {
  const key = await crypto.subtle.importKey("raw", encoder.encode(secret), {name:"HMAC",hash:"SHA-256"}, false, ["sign"]);
  return b64url(new Uint8Array(await crypto.subtle.sign("HMAC",key,encoder.encode(value))));
}
async function makeSession(secret) {
  const payload = b64url(encoder.encode(JSON.stringify({exp:Date.now()+7*24*60*60*1000,nonce:crypto.randomUUID()})));
  return payload + "." + await sign(payload,secret);
}
async function validSession(request, secret) {
  const raw = request.headers.get("Cookie") || "";
  const token = raw.split(";").map(x=>x.trim()).find(x=>x.startsWith(COOKIE+"="))?.slice(COOKIE.length+1);
  if (!token || !secret) return false;
  const parts = token.split(".");
  if (parts.length !== 2) return false;
  const expected = await sign(parts[0],secret);
  if (expected !== parts[1]) return false;
  try {
    const payload = JSON.parse(new TextDecoder().decode(fromB64url(parts[0])));
    return Number(payload.exp) > Date.now();
  } catch { return false; }
}
function cookie(value, maxAge=604800) {
  return `${COOKIE}=${value}; Path=/; Max-Age=${maxAge}; Secure; HttpOnly; SameSite=Strict`;
}
function tokenFor(repo, env) {
  return repo.startsWith("senthilsrinivasanmuthaiyan1/")
    ? env.GITHUB_TOKEN_SECONDARY
    : env.GITHUB_TOKEN_PRIMARY;
}
async function githubGet(path, repo, env) {
  const token = tokenFor(repo,env);
  if (!token) throw new Error("GitHub token missing for repository owner: "+repo.split("/")[0]);
  const response = await fetch("https://api.github.com"+path,{
    headers:{Authorization:"Bearer "+token,Accept:"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"ERP-Super-Agent"}
  });
  if (!response.ok) throw new Error("GitHub API "+response.status+" for "+path+": "+(await response.text()).slice(0,180));
  return response.json();
}
async function auditOne(project,env) {
  try {
    const [repo,pulls,branches] = await Promise.all([
      githubGet("/repos/"+project.repo,project.repo,env),
      githubGet("/repos/"+project.repo+"/pulls?state=open&per_page=100",project.repo,env),
      githubGet("/repos/"+project.repo+"/branches?per_page=100",project.repo,env)
    ]);
    return {project_key:project.key,name:project.name,repository:project.repo,status:"audited",
      default_branch:repo.default_branch,private:repo.private,updated_at:repo.updated_at,
      open_pull_requests:pulls.map(p=>({number:p.number,title:p.title,draft:p.draft,head:p.head.ref,base:p.base.ref,url:p.html_url})),
      branches:branches.map(b=>b.name),url:repo.html_url};
  } catch(error) {
    return {project_key:project.key,name:project.name,repository:project.repo,status:"blocked",blocker:error.message};
  }
}
async function saveRun(env,projectKey,type,status,request,result) {
  await env.DB.prepare("INSERT INTO runs(created_at,project_key,run_type,status,request,result_json) VALUES(?,?,?,?,?,?)")
    .bind(new Date().toISOString(),projectKey,type,status,request,JSON.stringify(result)).run();
}
async function modelText(env,system,user) {
  if (env.AI_ENABLED !== "true") return {enabled:false,answer:"AI inference is disabled. Set AI_ENABLED=true in Worker settings to use the Cloudflare Workers AI free daily allocation."};
  const result = await env.AI.run(MODEL,{messages:[{role:"system",content:system},{role:"user",content:user}],max_tokens:1200});
  return {enabled:true,answer:result.response || result.output_text || JSON.stringify(result)};
}
async function handleApi(request,env) {
  const url = new URL(request.url);
  if (url.pathname === "/api/login" && request.method === "POST") {
    const body = await request.json().catch(()=>({}));
    if (!env.ADMIN_PASSWORD || !env.SESSION_SECRET) return json({error:"Admin secrets are not configured."},503);
    if (typeof body.password !== "string" || body.password.length > 256 || body.password !== env.ADMIN_PASSWORD) return json({error:"Invalid password."},401);
    const session = await makeSession(env.SESSION_SECRET);
    return json({ok:true},{status:200,headers:{ "set-cookie":cookie(session) }});
  }
  if (url.pathname === "/api/health" && request.method === "GET") {
    return json({status:"ok",authenticated:await validSession(request,env.SESSION_SECRET||""),ai_enabled:env.AI_ENABLED==="true",model:MODEL});
  }
  if (url.pathname === "/api/logout" && request.method === "POST") {
    return json({ok:true},{status:200,headers:{"set-cookie":cookie("",0)}});
  }
  if (!await validSession(request,env.SESSION_SECRET||"")) return json({error:"Authentication required."},401);
  if (url.pathname === "/api/projects" && request.method === "GET") return json(PROJECTS);
  if (url.pathname === "/api/runs" && request.method === "GET") {
    const rows = await env.DB.prepare("SELECT id,created_at,project_key,run_type,status,request,result_json FROM runs ORDER BY id DESC LIMIT 30").all();
    return json((rows.results||[]).map(r=>({...r,result:JSON.parse(r.result_json)})));
  }
  if (url.pathname === "/api/audit" && request.method === "POST") {
    const results = await Promise.all(PROJECTS.map(p=>auditOne(p,env)));
    const ok = results.filter(r=>r.status==="audited").length;
    let analysis = {enabled:false,answer:"AI summary disabled."};
    try {
      analysis = await modelText(env,
        "You are the portfolio operations analyst for 11 ERP products. Use only supplied GitHub metadata. Separate facts from recommendations. Identify open PRs, branches and blockers. Never claim source code quality was checked.",
        "Summarize this live portfolio audit. Give priorities and blockers.\n"+JSON.stringify(results));
    } catch(e) { analysis={enabled:true,error:e.message}; }
    const result = {projects_total:PROJECTS.length,audited:ok,blocked:PROJECTS.length-ok,projects:results,analysis};
    await saveRun(env,null,"portfolio_audit",ok===PROJECTS.length?"completed":"partial","Audit all 11 ERP repositories",result);
    return json(result);
  }
  if (url.pathname === "/api/tasks" && request.method === "POST") {
    const body = await request.json().catch(()=>({}));
    const project = PROJECTS.find(p=>p.key===body.project_key);
    if (!project || typeof body.request!=="string" || body.request.trim().length<5 || body.request.length>4000) return json({error:"Select a valid project and enter a task of 5–4000 characters."},400);
    const role = ["router","auditor","competitor","implementer","reviewer"].includes(body.role)?body.role:"router";
    const prompt = "Project: "+project.name+" ("+project.repo+"). Mission: "+project.mission+". Role: "+role+". User request: "+body.request+". Produce an ordered, evidence-aware plan, acceptance criteria, risks and validation steps. This control plane is planning-only: do not claim that source files were changed, tests run, commits made or merges performed.";
    let answer;
    try { answer = await modelText(env,"You are a careful senior software delivery agent coordinating a multi-repository ERP portfolio.",prompt); }
    catch(e) { return json({error:"AI request failed: "+e.message},503); }
    const result={project_key:project.key,repository:project.repo,role,execution_state:"plan_only",...answer};
    await saveRun(env,project.key,role,"completed",body.request,result);
    return json(result);
  }
  return json({error:"Not found."},404);
}
export default {
  async fetch(request,env) {
    const url = new URL(request.url);
    if (url.pathname.startsWith("/api/")) {
      try { return await handleApi(request,env); }
      catch(error) { return json({error:error.message||"Internal error."},500); }
    }
    return env.ASSETS.fetch(request);
  }
};
