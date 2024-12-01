/* https://htmx.org/extensions/ws/ */
/* https://htmx.org/events/ */

function registerHtmxWsEventHandlers(el, eventHandlers) {
    const wsEventNames = [
        "htmx:wsConnecting", "htmx:wsOpen", "htmx:wsClose", "htmx:wsError",
        "htmx:wsBeforeMessage", "htmx:wsAfterMessage", "htmx:wsConfigSend", "htmx:wsBeforeSend",
        "htmx:wsAfterSend",
    ];
    wsEventNames.forEach(eventName => {
        const funcName = eventName.replace("htmx:", "");
        const handler = eventHandlers[funcName];
        if (handler) {
            el.addEventListener(eventName, handler.bind(eventHandlers));
        }
    });
}
