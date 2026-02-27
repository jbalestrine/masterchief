sub init()
    m.webView = m.top.findNode("webView")
    if m.webView <> invalid
        m.webView.visible = true
        m.webView.setFocus(true)
        m.webView.uri = "http://10.0.0.159:8080/roku"
    end if
end sub
