"""ajout champs users

Revision ID: e5c395fc7fa9
Revises: 
Create Date: 2026-06-10 15:38:20.588355
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'e5c395fc7fa9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Ajout des colonnes avec sa.String à la place de sqlmodel...
    op.add_column('user', sa.Column('nom', sa.String(length=100), nullable=False))
    op.add_column('user', sa.Column('prenom', sa.String(length=100), nullable=False))
    op.add_column('user', sa.Column('telephone', sa.String(length=20), nullable=False))
    op.add_column('user', sa.Column('photo_profil', sa.String(length=500), nullable=True))
    op.add_column('user', sa.Column('ville_id', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('adresse', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('statut', sa.Enum('ACTIVE', 'SUSPENDED', 'PENDING', name='userstatus'), nullable=False, server_default='PENDING'))
    # Pour les dates : on donne une valeur par défaut aux lignes existantes
    op.add_column('user', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('user', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')))
    
    # Modifier le type de la colonne role (si nécessaire)
    op.alter_column('user', 'role',
               existing_type=mysql.VARCHAR(length=255),
               type_=sa.Enum('ADMIN', 'TEACHER', 'STUDENT', name='userrole'),
               existing_nullable=False)
    
    # Ajouter une contrainte d'unicité sur telephone
    op.create_unique_constraint('uq_user_telephone', 'user', ['telephone'])
    
    # Supprimer les anciennes colonnes
    op.drop_column('user', 'is_active')
    op.drop_column('user', 'phone')


def downgrade() -> None:
    """Downgrade schema."""
    # Restaurer les anciennes colonnes
    op.add_column('user', sa.Column('phone', mysql.VARCHAR(length=50), nullable=True))
    op.add_column('user', sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False, server_default='1'))
    
    # Supprimer la contrainte d'unicité
    op.drop_constraint('uq_user_telephone', 'user', type_='unique')
    
    # Revenir au type VARCHAR pour role
    op.alter_column('user', 'role',
               existing_type=sa.Enum('ADMIN', 'TEACHER', 'STUDENT', name='userrole'),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=False)
    
    # Supprimer les nouvelles colonnes
    op.drop_column('user', 'updated_at')
    op.drop_column('user', 'created_at')
    op.drop_column('user', 'statut')
    op.drop_column('user', 'adresse')
    op.drop_column('user', 'ville_id')
    op.drop_column('user', 'photo_profil')
    op.drop_column('user', 'telephone')
    op.drop_column('user', 'prenom')
    op.drop_column('user', 'nom')