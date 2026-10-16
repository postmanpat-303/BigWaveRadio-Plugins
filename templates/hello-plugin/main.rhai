// Hello Plugin: a starting point. A panel button opens an in-window
// overlay with a circle that breathes with the music. Esc, any key or a
// click closes it (without the "hotkeys" permission every key closes it).
//
// Full API: https://github.com/postmanpat-303/BigWaveRadio/blob/main/docs/PLUGIN_GUIDE.md

fn on_load(ctx) {
    ctx.state.level = 0.0;
}

fn on_audio(ctx, a) {
    // Smooth the level so the circle glides instead of jumping.
    ctx.state.level = ctx.state.level * 0.85 + a.level * 0.15;
}

fn on_panel(ctx, ui) {
    ui.label("Hello from my first plugin!");
    if ui.button("Open the overlay") { ctx.open_overlay(false); }
}

fn on_overlay(ctx, draw) {
    draw.fill("#000000c0");
    let r = 0.1 + ctx.state.level * 0.25;
    draw.circle(0.5, 0.5, r, ctx.settings.color);
    draw.text_center(0.5, 0.9, "Hello, BigWave Radio! (any key closes)", 20.0, "#ffffff");
}

