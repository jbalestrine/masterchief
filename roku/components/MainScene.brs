sub init()
    m.webView = m.top.findNode("webView")
    if m.webView <> invalid
        m.webView.visible = true
        m.webView.setFocus(true)
        m.webView.uri = "http://ciacpu.myddns.me:8080/"
    end if
end sub
