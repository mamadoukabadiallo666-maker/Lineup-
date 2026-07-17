
    request.session['dark_mode'] = not request.session.get('dark_mode', False)
    return redirect('settings')

