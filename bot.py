import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, PhotoSize
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ParseMode

# লগিং চালু করা
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- আপনার তথ্য এখানে পরিবর্তন করুন ---
BOT_TOKEN = "7987529802:AAFJrc31acKN86KDffq0SvE4dB1uA1EERlI"  # <--- এখানে আপনার বট টোকেন দিন
ADMIN_USER_ID = 8072031254  # <--- এখানে আপনার টেলিগ্রাম ইউজার আইডি দিন
BKASH_NUMBER = "01768991959" # আপনার বিকাশ নম্বর
# -------------------------------------

# --- আপনার সব সার্ভিস (ক্যাটাগরি অনুযায়ী ভাগ করা) ---
SERVICES = {
    'facebook': {
        'name': 'Facebook সার্ভিসসমূহ 👤', # ক্যাটাগরির বাটন টেক্সট
        'items': { # এই ক্যাটাগরির সার্ভিস
            'fb_star_gift': {
                'name': 'Facebook - Star⭐Gift Unlimited (ID: 2626)',
                'price_per_1000': 2838.0, 
                'link_prompt': 'অনুগ্রহ করে আপনার ফেসবুক পেজ/প্রোফাইলের লিঙ্কটি দিন যেটিতে স্টার পাঠাতে চান।'
            },
            'fb_love_react': {
                'name': 'Facebook - Post Reaction ~ Love ❤️ (ID: 2040)',
                'price_per_1000': 50.0, 
                'link_prompt': 'অনুগ্রহ করে আপনার ফেসবুক পোস্টের লিঙ্কটি দিন যেটিতে Love রিয়্যাক্ট পাঠাতে চান।'
            },
            'fb_like_react': { 'name': 'Facebook - Post Likes 👍 (ID: 2039)', 'price_per_1000': 50.0, 'link_prompt': 'অনুগ্রহ করে আপনার ফেসবুক পোস্টের লিঙ্কটি দিন।' },
            'fb_wow_react': { 'name': 'Facebook - Post Reaction ~ wow 😮 (ID: 2041)', 'price_per_1000': 50.0, 'link_prompt': 'অনুগ্রহ করে আপনার ফেসবুক পোস্টের লিঙ্কটি দিন।' },
            'fb_care_react': { 'name': 'Facebook - Post Reaction ~ care 🥰 (ID: 2042)', 'price_per_1000': 50.0, 'link_prompt': 'অনুগ্রহ করে আপনার ফেসবুক পোস্টের লিঙ্কটি দিন।' },
            'fb_haha_react': { 'name': 'Facebook - Post Reaction ~ haha 😂 (ID: 2043)', 'price_per_1000': 50.0, 'link_prompt': 'অনুগ্রহ করে আপনার ফেসবুক পোস্টের লিঙ্কটি দিন।' }
        }
    },
    'tiktok': {
        'name': 'TikTok সার্ভিসসমূহ 🎵', # ক্যাটাগরির বাটন টেক্সট
        'items': { # এই ক্যাটাগরির সার্ভিস
            'tt_like': { 'name': 'TikTok Likes ❤️', 'price_per_1000': 10.0, 'link_prompt': 'অনুগ্রহ করে আপনার TikTok ভিডিও লিঙ্কটি দিন।' },
            'tt_view': { 'name': 'TikTok Views 👁️', 'price_per_1000': 7.0, 'link_prompt': 'অনুগ্রহ করে আপনার TikTok ভিডিও লিঙ্কটি দিন।' },
            'tt_follower': { 'name': 'TikTok Followers 👥', 'price_per_1000': 170.0, 'link_prompt': 'অনুগ্রহ করে আপনার TikTok প্রোফাইল লিঙ্কটি দিন।' }
        }
    },
    'telegram': {
        'name': 'Telegram সার্ভিসসমূহ 🚀', # ক্যাটাগরির বাটন টেক্সট
        'items': { # এই ক্যাটাগরির সার্ভিস
            'tg_sub': { 'name': 'Telegram Channel Subscriber (3 day) 🚀', 'price_per_1000': 5.0, 'link_prompt': 'অনুগ্রহ করে আপনার টেলিগ্রাম চ্যানেল লিঙ্কটি দিন (e.g., t.me/channelname)।' },
            'tg_member': { 'name': 'Telegram Group Member 👨‍👩‍👧‍👦', 'price_per_1000': 7.0, 'link_prompt': 'অনুগ্রহ করে আপনার টেলিগ্রাম গ্রুপ লিঙ্কটি দিন (Public Group)।' },
            'tg_premium': { 'name': 'Telegram Premium Member ⭐', 'price_per_1000': 300.0, 'link_prompt': 'অনুগ্রহ করে আপনার টেলিগ্রাম গ্রুপ/চ্যানেল লিঙ্কটি দিন।' },
            'tg_post_view': { 'name': 'Telegram Post Views (Last 1 Post) 👁️‍🗨️', 'price_per_1000': 2.0, 'link_prompt': 'অনুগ্রহ করে আপনার টেলিগ্রাম চ্যানেল লিঙ্কটি দিন (আমরা শেষ পোস্টে ভিউ দেব)।' }
        }
    }
}
# -----------------------------------------

# Conversation states বা ধাপ (একটি ধাপ বেড়েছে)
SELECT_CATEGORY, SELECT_SERVICE, QUANTITY, LINK, PAYMENT = range(5)

# /start কমান্ড
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "হ্যালো! আমি SMM সার্ভিস বট। 🤖\n"
        "অর্ডার করতে /order কমান্ড দিন।"
    )

# /order কমান্ড (অর্ডার শুরু)
async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ক্যাটাগরি সিলেক্ট করার জন্য বাটন মেনু দেখায়"""
    keyboard = []
    # SERVICES ডিকশনারি থেকে ক্যাটাগরি বাটন তৈরি করা
    for key, info in SERVICES.items():
        button = [InlineKeyboardButton(info['name'], callback_data=key)]
        keyboard.append(button)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "অনুগ্রহ করে নিচের তালিকা থেকে আপনার পছন্দের সার্ভিস ক্যাটাগরি সিলেক্ট করুন:",
        reply_markup=reply_markup
    )
    
    # পরবর্তী ধাপ: ক্যাটাগরি সিলেক্ট করা
    return SELECT_CATEGORY

# ধাপ ১: ক্যাটাগরি বাটন সিলেক্ট করার পর
async def category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ক্যাটাগরি সেভ করে এবং সেই ক্যাটাগরির সার্ভিস বাটন দেখায়"""
    query = update.callback_query
    await query.answer() 
    
    category_key = query.data
    
    # ক্যাটাগরি সেভ করা
    context.user_data['selected_category'] = category_key 
    
    # সার্ভিস বাটন তৈরি করা
    keyboard = []
    category_items = SERVICES[category_key]['items']
    for service_key, service_info in category_items.items():
        button = [InlineKeyboardButton(service_info['name'], callback_data=service_key)]
        keyboard.append(button)
    
    # একটি "Back" বাটন যোগ করা
    keyboard.append([InlineKeyboardButton("🔙 ফিরে যান (ক্যাটাগরি)", callback_data='go_back_category')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=f"আপনি **{SERVICES[category_key]['name']}** সিলেক্ট করেছেন।\n"
             "এখন নিচের সার্ভিসগুলো থেকে একটি সিলেক্ট করুন:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    # পরবর্তী ধাপ: সার্ভিস সিলেক্ট করা
    return SELECT_SERVICE

# ধাপ ২: সার্ভিস বাটন সিলেক্ট করার পর
async def service_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """সার্ভিস সেভ করে এবং পরিমাণ জানতে চায়"""
    query = update.callback_query
    await query.answer() 
    
    service_key = query.data
    
    # যদি ইউজার "ফিরে যান" বাটনে ক্লিক করে
    if service_key == 'go_back_category':
        # ক্যাটাগরি দেখানোর ফাংশনটি আবার কল করা
        await order_start(query, context) # এখানে query.message এর বদলে query ব্যবহার করা যায়
        # তবে order_start ফাংশনটি update.message আশা করে, তাই query.message ব্যবহার করা ভালো
        # অথবা order_start কে query.message দিয়ে কল করতে হবে।
        # সহজ উপায় হলো order_start এর ভেতরের কোড কপি করা।
        keyboard = []
        for key, info in SERVICES.items():
            button = [InlineKeyboardButton(info['name'], callback_data=key)]
            keyboard.append(button)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "অনুগ্রহ করে নিচের তালিকা থেকে আপনার পছন্দের সার্ভিস ক্যাটাগরি সিলেক্ট করুন:",
            reply_markup=reply_markup
        )
        return SELECT_CATEGORY # আগের ধাপে ফেরত যাওয়া


    try:
        category_key = context.user_data['selected_category']
        service_info = SERVICES[category_key]['items'][service_key]
    except KeyError:
        logger.warning(f"সার্ভিস খুঁজে পেতে সমস্যা: ক্যাটাগরি={context.user_data.get('selected_category')}, সার্ভিস={service_key}")
        await query.edit_message_text("দুঃখিত, একটি সমস্যা হয়েছে। অনুগ্রহ করে /order দিয়ে আবার চেষ্টা করুন।")
        context.user_data.clear()
        return ConversationHandler.END

    # ইউজার কী সিলেক্ট করেছে তা সেভ করা
    context.user_data['service'] = service_info
    
    await query.edit_message_text(
        text=f"আপনি সিলেক্ট করেছেন: **{service_info['name']}**\n"
             f"মূল্য: ৳{service_info['price_per_1000']} (প্রতি ১০০০)\n\n"
             "অনুগ্রহ করে, আপনি কতগুলো নিতে চান তার পরিমাণ লিখুন (যেমন: 1000, 2000)।\n\n"
             "যেকোনো সময় অর্ডার বাতিল করতে /cancel লিখুন।",
        parse_mode=ParseMode.MARKDOWN
    )
    # পরবর্তী ধাপ: পরিমাণ জানা
    return QUANTITY

# ধাপ ৩: পরিমাণ বা Quantity পাওয়ার পর
async def quantity_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """পরিমাণ সেভ করে এবং ফেসবুক লিঙ্ক চায়"""
    try:
        quantity = int(update.message.text)
        if quantity < 1:
            await update.message.reply_text("পরিমাণ 1 এর কম হতে পারে না। আবার চেষ্টা করুন।")
            return QUANTITY

        service_info = context.user_data['service']
        price_per_1000 = service_info['price_per_1000']
        
        price = (quantity / 1000) * price_per_1000
        
        context.user_data['quantity'] = quantity
        context.user_data['price'] = price
        
        link_prompt = service_info['link_prompt'] 
        
        await update.message.reply_text(
            f"পরিমাণ: {quantity}\n"
            f"মোট চার্জ: ৳{price:,.2f}\n\n" 
            f"{link_prompt}" 
        )
        return LINK
    except ValueError:
        await update.message.reply_text("অনুগ্রহ করে শুধু সংখ্যা লিখুন (যেমন: 1000)। আবার চেষ্টা করুন।")
        return QUANTITY
    except KeyError:
        await update.message.reply_text("দুঃখিত, কোনো একটি সমস্যা হয়েছে। অনুগ্রহ করে /order দিয়ে আবার শুরু করুন।")
        context.user_data.clear()
        return ConversationHandler.END

# ধাপ ৪: লিঙ্ক পাওয়ার পর
async def link_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """লিঙ্ক সেভ করে এবং পেমেন্টের জন্য বলে"""
    link = update.message.text
    context.user_data['link'] = link
    
    try:
        service_info = context.user_data['service']
        quantity = context.user_data['quantity']
        price = context.user_data['price']
    except KeyError:
        await update.message.reply_text("দুঃখিত, সেশন শেষ হয়ে গেছে। অনুগ্রহ করে /order দিয়ে আবার শুরু করুন।")
        context.user_data.clear()
        return ConversationHandler.END

    await update.message.reply_text(
        f"✅ **আপনার অর্ডারের তথ্য:**\n"
        f"------------------------------\n"
        f"**সার্ভিস:** {service_info['name']}\n"
        f"**পরিমাণ:** {quantity}\n"
        f"**লিঙ্ক:** {link}\n"
        f"**মোট চার্জ:** ৳{price:,.2f}\n"
        f"------------------------------\n\n"
        f"অনুগ্রহ করে নিচের নম্বরে ৳{price:,.2f} পেমেন্ট করুন:\n\n"
        f"**বিকাশ (পার্সোনাল):** `{BKASH_NUMBER}`\n\n"
        "(দোকান/এজেন্ট থেকে ক্যাশ-ইন করবেন না, শুধু সেন্ড মানি বা পার্সোনাল নম্বর থেকে পেমেন্ট করুন)\n\n"
        "পেমেন্ট করার পর, অনুগ্রহ করে **ট্রানজেকশন আইডি (TrxID)** অথবা পেমেন্টের একটি **স্ক্রিনশট** এখানে পাঠান।",
        parse_mode=ParseMode.MARKDOWN
    )
    return PAYMENT

# ধাপ ৫: পেমেন্ট প্রুফ পাওয়ার পর (ফাইনাল ধাপ)
async def process_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, payment_proof_text: str, photo_file_id: str = None) -> int:
    """পেমেন্ট তথ্য অ্যাডমিনকে পাঠায় এবং ইউজারকে কনফার্ম করে"""
    user = update.effective_user
    
    try:
        service_info = context.user_data.get('service', {})
        quantity = context.user_data.get('quantity', 'N/A')
        price = context.user_data.get('price', 0)
        link = context.user_data.get('link', 'N/A')
        service_name = service_info.get('name', 'N/A')
    except KeyError:
        await update.message.reply_text("দুঃখিত, সেশন শেষ হয়ে গেছে। অনুগ্রহ করে /order দিয়ে আবার শুরু করুন।")
        context.user_data.clear()
        return ConversationHandler.END

    await update.message.reply_text(
        "আপনার পেমেন্টের তথ্যটি পেয়েছি। ✅\n"
        "অ্যাডমিন এটি যাচাই করে খুব শীঘ্রই আপনার অর্ডারটি কম্লিট করে দেবে।\n"
        "ধন্যবাদ!"
    )

    user_details = f"নাম: {user.full_name}"
    if user.username:
        user_details += f"\nইউজারনেম: @{user.username}"
    user_details += f"\nইউজার আইডি: `{user.id}`"

    admin_message = (
        f"🚨 **নতুন অর্ডার এসেছে!** 🚨\n\n"
        f"**মেম্বারের তথ্য:**\n{user_details}\n\n"
        f"**অর্ডারের তথ্য:**\n"
        f"সার্ভিস: **{service_name}**\n"
        f"পরিমাণ: {quantity}\n"
        f"চার্জ: ৳{price:,.2f}\n"
        f"লিঙ্ক: {link}\n\n"
        f"**পেমেন্ট তথ্য:**\n"
        f"{payment_proof_text}"
    )

    try:
        if photo_file_id:
            await context.bot.send_photo( chat_id=ADMIN_USER_ID, photo=photo_file_id, caption=admin_message, parse_mode=ParseMode.MARKDOWN )
        else:
            await context.bot.send_message( chat_id=ADMIN_USER_ID, text=admin_message, parse_mode=ParseMode.MARKDOWN )
    except Exception as e:
        logger.error(f"অ্যাডমিনকে মেসেজ পাঠাতে সমস্যা হয়েছে: {e}")
        await context.bot.send_message( chat_id=ADMIN_USER_ID, text=f"একটি অর্ডার নোটিফিকেশন পাঠাতে ফেইল হয়েছে। ইউজার আইডি: {user.id}" )

    context.user_data.clear()
    return ConversationHandler.END

# যদি ইউজার TrxID টেক্সট হিসাবে পাঠায়
async def payment_received_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    trx_id = update.message.text
    payment_proof = f"TrxID: `{trx_id}`"
    return await process_payment(update, context, payment_proof)

# যদি ইউজার স্ক্রিনশট (ছবি) পাঠায়
async def payment_received_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photo: PhotoSize = update.message.photo[-1]
    payment_proof = "পেমেন্ট স্ক্রিনশট (ছবিতে দেখুন)"
    return await process_payment(update, context, payment_proof, photo_file_id=photo.file_id)

# /cancel কমান্ড
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """কনভারসেশন বাতিল করে"""
    if update.callback_query:
        await update.callback_query.edit_message_text("অর্ডার বাতিল করা হয়েছে।")
    else:
        await update.message.reply_text("অর্ডার বাতিল করা হয়েছে।")
        
    context.user_data.clear()
    return ConversationHandler.END

# প্রধান ফাংশন (বট চালু করার জন্য)
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    # Conversation Handler সেটআপ (এখন ৫টি ধাপ)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("order", order_start)],
        states={
            # ধাপ ০: ক্যাটাগরি সিলেক্ট করা
            SELECT_CATEGORY: [CallbackQueryHandler(category_selected)],
            # ধাপ ১: সার্ভিস সিলেক্ট করা
            SELECT_SERVICE: [CallbackQueryHandler(service_selected)],
            # ধাপ ২: পরিমাণ লেখা
            QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, quantity_received)],
            # ধাপ ৩: লিঙ্ক লেখা
            LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, link_received)],
            # ধাপ ৪: পেমেন্ট প্রুফ দেওয়া
            PAYMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, payment_received_text),
                MessageHandler(filters.PHOTO, payment_received_photo)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    
    print("ক্যাটাগরি সহ আপগ্রেডেড বট চালু হচ্ছে... (বন্ধ করতে Ctrl+C চাপুন)")
    
    application.run_polling()

if __name__ == '__main__':
    main()
