odoo.define("connector_clickup.custom", function (require) {
    "use strict";

    var core = require("web.core");

    core.action_registry.add("redirect_with_code", function (action) {
        var redirectUrl = action.params.url;
        var parser = document.createElement("a");
        parser.href = redirectUrl;

        // Create an iframe and set the URL to the authorization URL
        var iframe = document.createElement("iframe");
        iframe.style.display = "none";
        iframe.src = redirectUrl;
        document.body.appendChild(iframe);

        // Listen for changes in the iframe URL
        iframe.addEventListener("load", function () {
            // Get the current URL from the iframe
            var iframeUrl = iframe.contentWindow.location.href;

            // Extract the code from the URL
            var urlParams = new URLSearchParams(iframeUrl);
            var authorizationCode = urlParams.get("code");

            // Send the code back to the server
            core.bus.trigger("authorization_code_received", authorizationCode);

            // Remove the iframe from the DOM
            document.body.removeChild(iframe);
        });

        return Promise.resolve();
    });
});
