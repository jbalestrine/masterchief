' ============================================================
'  MasterChief TV - Roku Channel
'  Loads ciacpi.myddns.me:8080 via roHtmlWidget
' ============================================================
sub Main(args as Dynamic)
    port = CreateObject("roMessagePort")

    rect   = CreateObject("roRectangle", 0, 0, 1280, 720)
    widget = CreateObject("roHtmlWidget", rect, {})
    widget.SetPort(port)
    widget.SetUrl("http://ciacpu.myddns.me:8080")
    widget.SetFocusable(true)
    widget.SetFocus(true)

    while true
        msg = Wait(0, port)
        if type(msg) = "roHtmlWidgetEvent"
            data = msg.GetData()
            if data.reason = "exit" or data.reason = "load-error"
                exit while
            end if
        else if type(msg) = "roUniversalControlEvent"
            key = msg.GetInt()
            if key = 0 or key = 10 then exit while
        end if
    end while
end sub
