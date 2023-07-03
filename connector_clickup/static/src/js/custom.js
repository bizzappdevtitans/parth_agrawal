odoo.define("connector_clickup.custom", function (require) {
    "use strict";

    var core = require("web.core");

    $(document).ready(function () {
        core.action_registry.add("redirect_with_code", function (action) {
            var redirectUrl = action.url; // Check the spelling and case sensitivity
            console.log("URL:", redirectUrl);

            var iframe = document.createElement("iframe");
            iframe.src = redirectUrl;
            iframe.style.width = "100%";
            iframe.style.height = "100%";
            iframe.style.border = "none";
            document.body.appendChild(iframe);

            iframe.addEventListener("load", function () {
                // Get the current URL from the iframe
                var iframeUrl = iframe.contentWindow.location.href;
                console.log("Iframe URL:", iframeUrl);

                // Extract the code from the URL
                var urlParams = new URLSearchParams(iframeUrl);
                var authorizationCode = urlParams.get("code");
                console.log("Authorization Code:", authorizationCode);

                // Send the code back to the server
                core.bus.trigger("authorization_code_received", authorizationCode);

                // Remove the iframe from the DOM
                document.body.removeChild(iframe);
            });

            return Promise.resolve();
        });
    });
});
