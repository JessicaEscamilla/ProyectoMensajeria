from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, send_file
)
from app.auth import login_required
from app.db import get_db

bp = Blueprint('inbox', __name__, url_prefix='/inbox')

@bp.route("/getDB")
@login_required
def getDB():
    return send_file(current_app.config['DATABASE'], as_attachment=True)

@bp.route('/show')
@login_required
def show():
    db = get_db()
    messages = db.execute(
        'select *, user.username from message inner join user on user.id = message.from_id where to_id = ?',(g.user['id'], )
    ).fetchall()
    return render_template('inbox/show.html', messages=messages)

@bp.route('/send', methods=['GET', 'POST'])
@login_required
def send():
    try:
        if request.method == 'POST':        
            from_id = g.user['id']
            to_username = request.form['to'] 
            subject = request.form['subject'] 
            body = request.form['body'] 
            db = get_db()
            if not to_username:
                flash('El detinatario es obligatorio')
                return render_template('inbox/send.html')
            if not subject:
                flash('El asunto es obligatorio')
                return render_template('inbox/send.html')
            if not body:
                flash('El contenido es obligatorio')
                return render_template('inbox/send.html')    
            error = None    
            userto = None 
            userto = db.execute(
                'select * from user where username = ?', (to_username,)
            ).fetchone()
            if userto is None:
                error = 'El destinatario no existe'
            if error is not None:
                flash(error)
            else:
                db = get_db()
                db.execute(
                    'insert into message (from_id, to_id, subject, body) values(?,?,?,?)',
                    (from_id, userto['id'], subject, body)
                )
                db.commit()
                return redirect(url_for('inbox.show'))
    except Exception as e:
        flash(str(e))
    return render_template('inbox/send.html')