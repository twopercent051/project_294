from create_bot import bot


async def file_sender(file_id, file_type, chat_id, caption=None, kb=None):
    if file_type == 'photo':
        await bot.send_photo(chat_id, photo=file_id, caption=caption, reply_markup=kb)
    if file_type == 'video':
        await bot.send_video(chat_id, video=file_id, caption=caption, reply_markup=kb)
    if file_type == 'video_note':
        await bot.send_video_note(chat_id, video_note=file_id, caption=caption, reply_markup=kb)
    if file_type == 'document':
        await bot.send_document(chat_id, document=file_id, caption=caption, reply_markup=kb)
    if file_type == 'audio':
        await bot.send_audio(chat_id, audio=file_id, caption=caption, reply_markup=kb)
    if file_type == 'voice':
        await bot.send_voice(chat_id, voice=file_id, caption=caption, reply_markup=kb)
    if file_type == 'animation':
        await bot.send_animation(chat_id, animation=file_id, caption=caption, reply_markup=kb)
