frappe.ready(() => {
    console.log("klendknew")
    const hideWorkspaceButtons = () => {
        // Hide "Create Workspace" button
        document.querySelectorAll('button').forEach(btn => {
            if (btn.innerText.trim() === "Create Workspace") {
                btn.style.display = "none";
            }
        });

        // Hide "Edit" button
        document.querySelectorAll('button').forEach(btn => {
            if (btn.innerText.trim() === "Edit") {
                btn.style.display = "none";
            }
        });
    };

    // Run once after load
    hideWorkspaceButtons();

    // Also watch DOM changes (because Frappe redraws desk dynamically)
    const observer = new MutationObserver(hideWorkspaceButtons);
    observer.observe(document.body, { childList: true, subtree: true });
});
