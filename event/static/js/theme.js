document.addEventListener("DOMContentLoaded", function () {

const root=document.documentElement;

const themeBtn=document.getElementById("themeBtn");
const themePanel=document.getElementById("themePanel");

if(themeBtn&&themePanel){
themeBtn.onclick=function(){
themePanel.classList.toggle("open");
};
}

const themes={
blue:{
primary:"#2563eb",
hover:"#1d4ed8",
success:"#059669",
successHover:"#047857"
},
green:{
primary:"#10b981",
hover:"#059669",
success:"#10b981",
successHover:"#059669"
},
red:{
primary:"#ef4444",
hover:"#dc2626",
success:"#ef4444",
successHover:"#dc2626"
},
orange:{
primary:"#f97316",
hover:"#ea580c",
success:"#f97316",
successHover:"#ea580c"
},
purple:{
primary:"#8b5cf6",
hover:"#7c3aed",
success:"#8b5cf6",
successHover:"#7c3aed"
}
};

function applyTheme(theme){

root.style.setProperty("--primary-color",theme.primary);
root.style.setProperty("--hover-color",theme.hover);

root.style.setProperty("--success-color",theme.success);
root.style.setProperty("--success-hover",theme.successHover);

localStorage.setItem("customTheme", JSON.stringify(theme));

}

const savedTheme=localStorage.getItem("customTheme");

if(savedTheme){
applyTheme(JSON.parse(savedTheme));
}

document.querySelectorAll(".color").forEach(function(btn){

btn.onclick=function(){

const color=this.classList[1];

applyTheme(themes[color]);

};

});

document.querySelectorAll(".sidebar-color").forEach(function(btn){

btn.onclick=function(){

const color=this.dataset.sidebar;

root.style.setProperty("--sidebar-color",color);

if(color=="#000"){
root.style.setProperty("--sidebar-hover","#111111");
}
else if(color=="#1e3a8a"){
root.style.setProperty("--sidebar-hover","#2949a8");
}
else{
root.style.setProperty("--sidebar-hover","#4b5563");
}

localStorage.setItem("sidebar",color);

};

});

const savedSidebar=localStorage.getItem("sidebar");

if(savedSidebar){

root.style.setProperty("--sidebar-color",savedSidebar);

if(savedSidebar=="#000"){
root.style.setProperty("--sidebar-hover","#111111");
}
else if(savedSidebar=="#1e3a8a"){
root.style.setProperty("--sidebar-hover","#2949a8");
}
else{
root.style.setProperty("--sidebar-hover","#4b5563");
}

}

const fontFamily=document.getElementById("fontFamily");

if(fontFamily){

const savedFont=localStorage.getItem("font");

if(savedFont){

document.body.style.fontFamily=savedFont;

fontFamily.value=savedFont;

}

fontFamily.onchange=function(){

document.body.style.fontFamily=this.value;

localStorage.setItem("font",this.value);

};

}

const fontSize=document.getElementById("fontSize");

if(fontSize){

const savedSize=localStorage.getItem("fontSize");

if(savedSize){

document.body.style.fontSize=savedSize+"px";

fontSize.value=savedSize;

}

fontSize.oninput=function(){

document.body.style.fontSize=this.value+"px";

localStorage.setItem("fontSize",this.value);

};

}

const reset=document.getElementById("resetTheme");

if(reset){

reset.onclick=function(){

localStorage.clear();

location.reload();

};

}

});

document.addEventListener("DOMContentLoaded", function () {

    // Existing theme code...

    const developerBtn = document.getElementById("developerBtn");
    const developerModal = document.getElementById("developerModal");
    const closeDeveloper = document.querySelector(".close-developer");

    if (developerBtn) {
        developerBtn.addEventListener("click", function (e) {
            e.preventDefault();
            developerModal.classList.add("show");
        });
    }

    if (closeDeveloper) {
        closeDeveloper.addEventListener("click", function () {
            developerModal.classList.remove("show");
        });
    }

});


