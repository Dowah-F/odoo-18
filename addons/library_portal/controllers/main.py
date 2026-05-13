# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import werkzeug

class LibraryController(http.Controller):

    # ==========================================================
    # PHẦN 2: HTTP CONTROLLERS (Giao diện Web / Frontend)
    # ==========================================================

    # Yêu cầu 2.1 – Trang danh sách sách
    @http.route('/library/books', type='http', auth='public', website=True)
    def library_books(self, **kw):
        # Lấy các sách đang có sẵn
        books = request.env['library.book'].sudo().search([('state', '=', 'available')])
        # Render template QWeb
        return request.render('library_portal.books_list_template', {
            'books': books
        })

    # Yêu cầu 2.2 – Trang chi tiết sách
    @http.route('/library/book/<int:id>', type='http', auth='public', website=True)
    def library_book_detail(self, id, **kw):
        book = request.env['library.book'].sudo().browse(id)
        # Xử lý trường hợp sách không tồn tại (trả về 404)
        if not book.exists():
            raise werkzeug.exceptions.NotFound()
        
        return request.render('library_portal.book_detail_template', {
            'book': book
        })

    # Yêu cầu 2.3 – Form đăng ký mượn sách (Route GET: Hiển thị form)
    @http.route('/library/borrow/<int:book_id>', type='http', auth='public', website=True)
    def library_borrow_form(self, book_id, **kw):
        book = request.env['library.book'].sudo().browse(book_id)
        if not book.exists() or book.quantity <= 0:
            raise werkzeug.exceptions.NotFound()
            
        return request.render('library_portal.borrow_form_template', {
            'book': book,
            'error': None,       # Truyền biến error rỗng khi mới vào trang
            'post_data': {}      # Truyền biến post_data rỗng để không bị lỗi field
        })

    # Yêu cầu 2.3 – Xử lý form đăng ký mượn (Route POST: Nhận dữ liệu)
    @http.route('/library/borrow/submit', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def library_borrow_submit(self, **post):
        book_id = int(post.get('book_id', 0))
        name = post.get('name', '').strip()
        email = post.get('email', '').strip()
        phone = post.get('phone', '').strip()
        
        book = request.env['library.book'].sudo().browse(book_id)
        
        # 1. Validate dữ liệu
        error = None
        if not name:
            error = "Họ và tên không được để trống!"
        elif '@' not in email:
            error = "Email không hợp lệ (phải chứa ký tự @)!"
            
        # 2. Nếu dữ liệu lỗi: Render lại form, hiện lỗi và giữ nguyên giá trị đã nhập
        if error:
            return request.render('library_portal.borrow_form_template', {
                'book': book,
                'error': error,
                'post_data': post  # Trả lại dict post để template gán lại vào value=""
            })
            
        # 3. Nếu hợp lệ: Lưu vào database (Model)
        borrow_req = request.env['library.borrow.request'].sudo().create({
            'name': name,
            'email': email,
            'phone': phone,
            'book_id': book.id,
        })
        
        # 4. Redirect sang trang cảm ơn để tránh gửi lại form khi F5
        return request.redirect(f'/library/borrow/thank-you?request_id={borrow_req.id}')

    # Trang cảm ơn sau khi submit form
    @http.route('/library/borrow/thank-you', type='http', auth='public', website=True)
    def library_borrow_thank_you(self, request_id=None, **kw):
        return request.render('library_portal.borrow_thank_you_template', {
            'request_id': request_id
        })


    # ==========================================================
    # PHẦN 3: JSON CONTROLLERS (API trả về dữ liệu dạng JSON)
    # ==========================================================

    # Yêu cầu 3.1 – API lấy danh sách sách
    @http.route('/api/library/books', type='json', auth='public')
    def api_get_books(self, **kw):
        # Dùng search_read để trả thẳng ra list chứa dict (JSON array)
        books = request.env['library.book'].sudo().search_read(
            [('state', '=', 'available')],
            ['id', 'name', 'author', 'quantity']
        )
        return books

    # Yêu cầu 3.2 – API tạo borrow request (Nhận JSON input)
    @http.route('/api/library/borrow', type='json', auth='public')
    def api_create_borrow(self, **kw):
        book_id = kw.get('book_id')
        name = kw.get('name')
        email = kw.get('email')
        phone = kw.get('phone')
        
        # Validate bắt buộc
        if not all([book_id, name, email]):
            return {"success": False, "error": "Thiếu dữ liệu bắt buộc (book_id, name, email)"}
            
        book = request.env['library.book'].sudo().browse(int(book_id))
        
        # Validate logic nghiệp vụ
        if not book.exists():
            return {"success": False, "error": "Sách không tồn tại"}
        if book.quantity <= 0:
            return {"success": False, "error": "Sách đã hết"}
            
        # Lưu vào Model và trả về kết quả
        try:
            borrow_req = request.env['library.borrow.request'].sudo().create({
                'name': name,
                'email': email,
                'phone': phone,
                'book_id': book.id,
            })
            return {"success": True, "request_id": borrow_req.id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Yêu cầu 3.3 – API yêu cầu đăng nhập
    @http.route('/api/library/my-requests', type='json', auth='user')
    def api_my_requests(self, **kw):
        # auth='user' đảm bảo route này chỉ chạy khi đã đăng nhập
        current_user = request.env.user
        
        if not current_user.email:
            return {"error": "Người dùng hiện tại chưa cấu hình email trong hệ thống."}
            
        # Lọc danh sách mượn theo email của user đang đăng nhập
        requests = request.env['library.borrow.request'].search_read(
            [('email', '=', current_user.email)],
            ['id', 'name', 'book_id', 'state', 'request_date']
        )
        return requests