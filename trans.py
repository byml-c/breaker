from premailer import transform

# 将样式表转化为内联样式，使其能在邮件中被显示
with open('./html/notice-body.html', 'r', encoding='utf-8') as f_in:
    a = transform(f_in.read())
with open('./html/notice-body-linear.html', 'w', encoding='utf-8') as f_out:
    f_out.write(a)
print('Finish!')