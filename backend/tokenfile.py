def save_token(token):
    print('Saving Token')
    with open("token.txt", 'w') as f:
        f.seek(0)
        f.write(str(token))
        f.truncate()
    return