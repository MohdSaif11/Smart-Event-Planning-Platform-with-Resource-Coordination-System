document.addEventListener("DOMContentLoaded", function () {
    const root = document.documentElement;

    const themeBtn = document.getElementById("themeBtn");
    const themePanel = document.getElementById("themePanel");

    if (themeBtn && themePanel) {
        themeBtn.addEventListener("click", function () {
            themePanel.classList.toggle("open");
        });
    }

    const themes = {
        blue: {
            primary: "#2563eb",
            hover: "#1d4ed8",
            success: "#059669",
            successHover: "#047857"
        },
        green: {
            primary: "#10b981",
            hover: "#059669",
            success: "#10b981",
            successHover: "#059669"
        },
        red: {
            primary: "#ef4444",
            hover: "#dc2626",
            success: "#ef4444",
            successHover: "#dc2626"
        },
        orange: {
            primary: "#f97316",
            hover: "#ea580c",
            success: "#f97316",
            successHover: "#ea580c"
        },
        purple: {
            primary: "#8b5cf6",
            hover: "#7c3aed",
            success: "#8b5cf6",
            successHover: "#7c3aed"
        }
    };

    function applyTheme(theme) {
        if (!theme) {
            return;
        }

        root.style.setProperty("--primary-color", theme.primary);
        root.style.setProperty("--hover-color", theme.hover);
        root.style.setProperty("--success-color", theme.success);
        root.style.setProperty("--success-hover", theme.successHover);

        localStorage.setItem("customTheme", JSON.stringify(theme));
    }

    const savedTheme = localStorage.getItem("customTheme");

    if (savedTheme) {
        try {
            applyTheme(JSON.parse(savedTheme));
        } catch (error) {
            localStorage.removeItem("customTheme");
        }
    }

    document.querySelectorAll(".color").forEach(function (button) {
        button.addEventListener("click", function () {
            const selectedColor = this.dataset.color;

            const themeName = Object.keys(themes).find(function (name) {
                return themes[name].primary === selectedColor;
            });

            if (themeName) {
                applyTheme(themes[themeName]);
            }
        });
    });

    function applySidebarColor(color) {
        root.style.setProperty("--sidebar-color", color);

        if (color === "#000") {
            root.style.setProperty("--sidebar-hover", "#111111");
        } else if (color === "#1e3a8a") {
            root.style.setProperty("--sidebar-hover", "#2949a8");
        } else {
            root.style.setProperty("--sidebar-hover", "#4b5563");
        }
    }

    document.querySelectorAll(".sidebar-color").forEach(function (button) {
        button.addEventListener("click", function () {
            const color = this.dataset.sidebar;

            applySidebarColor(color);

            localStorage.setItem("sidebar", color);
        });
    });

    const savedSidebar = localStorage.getItem("sidebar");

    if (savedSidebar) {
        applySidebarColor(savedSidebar);
    }

    const fontFamily = document.getElementById("fontFamily");

    if (fontFamily) {
        const savedFont = localStorage.getItem("font");

        if (savedFont) {
            document.body.style.fontFamily = savedFont;
            fontFamily.value = savedFont;
        }

        fontFamily.addEventListener("change", function () {
            document.body.style.fontFamily = this.value;

            localStorage.setItem("font", this.value);
        });
    }

    const fontSize = document.getElementById("fontSize");

    if (fontSize) {
        const savedSize = localStorage.getItem("fontSize");

        if (savedSize) {
            document.body.style.fontSize = savedSize + "px";
            fontSize.value = savedSize;
        }

        fontSize.addEventListener("input", function () {
            document.body.style.fontSize = this.value + "px";

            localStorage.setItem("fontSize", this.value);
        });
    }

    const resetTheme = document.getElementById("resetTheme");

    if (resetTheme) {
        resetTheme.addEventListener("click", function () {
            localStorage.removeItem("customTheme");
            localStorage.removeItem("sidebar");
            localStorage.removeItem("font");
            localStorage.removeItem("fontSize");

            root.style.removeProperty("--primary-color");
            root.style.removeProperty("--hover-color");
            root.style.removeProperty("--success-color");
            root.style.removeProperty("--success-hover");
            root.style.removeProperty("--sidebar-color");
            root.style.removeProperty("--sidebar-hover");

            document.body.style.fontFamily = "";
            document.body.style.fontSize = "";

            location.reload();
        });
    }

    const developerBtn = document.getElementById("developerBtn");
    const developerModal = document.getElementById("developerModal");
    const closeDeveloper = document.querySelector(".close-developer");

    if (developerBtn && developerModal) {
        developerBtn.addEventListener("click", function (event) {
            event.preventDefault();

            developerModal.classList.add("show");
        });
    }

    if (closeDeveloper && developerModal) {
        closeDeveloper.addEventListener("click", function () {
            developerModal.classList.remove("show");
        });
    }

    if (developerModal) {
        developerModal.addEventListener("click", function (event) {
            if (event.target === developerModal) {
                developerModal.classList.remove("show");
            }
        });
    }
});
