local function handler (elem)
    -- Get the length of the content
    Len = #elem.content
    -- Check that the content isn't empty
    if 0 < Len then
        -- Is the last child a space?
        if 'Space' == elem.content[Len].tag then
            -- Remove the space (last child)
            elem.content:remove()
        -- Return a space *after* the element
            return { elem, pandoc.Space() }
        end
    end
    return nil
end

return {
    {
        Emph      = handler,
        Strong    = handler,
        Strikeout = handler,
        SmallCaps = handler,
        Underline = handler,
        Span      = handler,
        Link      = handler,
    }
}