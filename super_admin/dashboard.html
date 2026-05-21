<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Super Admin</title>

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body { background:#0f172a; color:#e2e8f0; }

.sidebar {
    width:240px; height:100vh; position:fixed;
    background:#020617;
}

.sidebar a {
    display:block; padding:12px; color:#cbd5f5;
}
.sidebar a:hover { background:#1e293b; }

.content { margin-left:240px; padding:20px; }

.card { background:#1e293b; border-radius:12px; }
.table { color:white; }

.topbar {
    background:#020617; padding:10px;
    display:flex; justify-content:space-between;
}

.badge-active { background:green; }
.badge-blocked { background:red; }
</style>
</head>

<body>

<!-- SIDEBAR -->
<div class="sidebar">
    <h4 class="text-center text-white mt-3">👑 Super</h4>
    <a onclick="loadDashboard()">🏠 Dashboard</a>
    <a onclick="loadAdmins()">👨‍💼 Admins</a>
    <a onclick="loadLogs()">🧠 Logs</a>
</div>

<!-- CONTENT -->
<div class="content">

<div class="topbar">
    <span>🚀 Super Admin Panel</span>
    <button class="btn btn-danger btn-sm" onclick="logout()">Logout</button>
</div>

<h3 id="title" class="mt-3">Dashboard</h3>

<input id="search" class="form-control mb-3" placeholder="Search...">

<div id="main"></div>

</div>

<script>

// ================= DASHBOARD =================
function loadDashboard() {

    document.getElementById("title").innerText = "Dashboard";

    fetch('/super/analytics')
    .then(r=>r.json())
    .then(res=>{
        let d = res.data;

        document.getElementById("main").innerHTML = `
        <div class="row text-center">

            <div class="col-md-3">
                <div class="card p-3">
                    <h6>Total Users</h6>
                    <h2>${d.users.total}</h2>
                </div>
            </div>

            <div class="col-md-3">
                <div class="card p-3">
                    <h6>Active</h6>
                    <h2>${d.users.active}</h2>
                </div>
            </div>

            <div class="col-md-3">
                <div class="card p-3">
                    <h6>Blocked</h6>
                    <h2>${d.users.blocked}</h2>
                </div>
            </div>

            <div class="col-md-3">
                <div class="card p-3">
                    <h6>Admins</h6>
                    <h2>${d.admins.total}</h2>
                </div>
            </div>

        </div>

        <div class="card mt-4 p-3">
            <canvas id="chart"></canvas>
        </div>
        `;

        new Chart(document.getElementById("chart"), {
            type:'line',
            data:{
                labels:d.growth.map(g=>g.date),
                datasets:[{
                    label:'User Growth',
                    data:d.growth.map(g=>g.count)
                }]
            }
        });
    });
}


// ================= ADMINS =================
function loadAdmins(page=1){

    document.getElementById("title").innerText="Admins";

    fetch(`/super/admins?page=${page}`)
    .then(r=>r.json())
    .then(res=>{

        let html = `
        <table class="table">
        <tr><th>ID</th><th>Name</th><th>Status</th><th>Action</th></tr>
        `;

        res.data.admins.forEach(a=>{
            html+=`
            <tr>
                <td>${a.id}</td>
                <td>${a.name}</td>
                <td>
                    <span class="badge ${a.status=='active'?'badge-active':'badge-blocked'}">
                        ${a.status}
                    </span>
                </td>
                <td>
                    <button onclick="updateAdmin(${a.id},'approve')" class="btn btn-success btn-sm">✔</button>
                    <button onclick="updateAdmin(${a.id},'block')" class="btn btn-danger btn-sm">✖</button>
                </td>
            </tr>
            `;
        });

        html += "</table>";

        document.getElementById("main").innerHTML=html;
    });
}


// ================= UPDATE =================
function updateAdmin(id,action){
    fetch(`/super/admin/${id}/status`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({action})
    }).then(()=>loadAdmins());
}


// ================= LOGS =================
function loadLogs(){

    document.getElementById("title").innerText="Logs";

    fetch('/super/logs')
    .then(r=>r.json())
    .then(res=>{

        let html = `
        <table class="table">
        <tr><th>Actor</th><th>Target</th><th>Action</th><th>Time</th></tr>
        `;

        res.data.logs.forEach(l=>{
            html+=`
            <tr>
                <td>${l.actor}</td>
                <td>${l.target}</td>
                <td>${l.action}</td>
                <td>${l.time}</td>
            </tr>
            `;
        });

        html+="</table>";

        document.getElementById("main").innerHTML=html;
    });
}


// ================= LOGOUT =================
function logout(){
    window.location="/logout";
}


// INIT
loadDashboard();

</script>

</body>
</html>
