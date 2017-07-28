def process_message(message):
    if message.get('type') == 'ChatMessage':
        res_type = 'message'
        return [res_type, message['message']['text']]

    elif message.get('type') == 'AgentTyping':
        pass

    elif message.get('type') == 'AgentNotTyping':
        pass

    elif message.get('type') == 'AgentDisconnect':
        pass

    elif message.get('type') == 'ChasitorSessionData':
        pass

    elif message.get('type') == 'ChatEnded':
        res_type = 'end'
        return [res_type, '接続が終了しました。']

    elif message.get('type') == 'ChatEstablished':
        pass

    elif message.get('type') == 'ChatRequestFail':
        res_type = 'fail'
        return [res_type, 'ただいま接続できません。']

    elif message.get('type') == 'ChatRequestSuccess':
        res_type = 'ok'
        return [res_type, '接続しました。']

    elif message.get('type') == 'ChatTransferred':
        pass

    elif message.get('type') == 'CustomEvent':
        pass

    elif message.get('type') == 'NewVisitorBreadcrumb':
        pass

    elif message.get('type') == 'QueueUpdate':
        pass

    elif message.get('type') == 'FileTransfer':
        pass

    elif message.get('type') == 'Availability':
        pass

    return [None, None]
