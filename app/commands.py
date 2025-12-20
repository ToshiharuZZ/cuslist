"""
CLIコマンド定義
"""
import click
from flask.cli import with_appcontext
from app.services.cancellation_service import CancellationService

@click.command('cleanup-accounts')
@with_appcontext
def cleanup_accounts_command():
    """保持期限が切れた解約アカウントをクリーンアップする"""
    service = CancellationService()
    count = service.cleanup_expired_accounts()
    click.echo(f"Cleanup completed. {count} accounts removed.")

def init_app_commands(app):
    """コマンドをアプリケーションに登録"""
    app.cli.add_command(cleanup_accounts_command)
