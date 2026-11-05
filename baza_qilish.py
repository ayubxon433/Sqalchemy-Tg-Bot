
from sqlalchemy import (
    create_engine, Integer, String, Float, Boolean,
    DateTime, select, delete, update
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, Session
)
from datetime import datetime


# DATABASE
engine = create_engine("sqlite:///products.db")


class Base(DeclarativeBase):
    pass


# MAHSULOTLAR JADVALI
class Products(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float)
    quantity: Mapped[int] = mapped_column(Integer)
    country: Mapped[str] = mapped_column(String)
    image: Mapped[str] = mapped_column(String)


# BUYURTMALAR JADVALI
class Buyurtma(Base):
    __tablename__ = "buyurtma"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    egasi: Mapped[int] = mapped_column(Integer)
    mahsulot: Mapped[int] = mapped_column(Integer)

    miqdori: Mapped[int] = mapped_column(Integer)
    summa: Mapped[float] = mapped_column(Float)

    status: Mapped[str] = mapped_column(
        String, default="cart"
    )

    vaqt: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )

    ism: Mapped[str] = mapped_column(
        String, default=""
    )

    telefon: Mapped[str] = mapped_column(
        String, default=""
    )

    manzil: Mapped[str] = mapped_column(
        String, default=""
    )


# JADVALLARNI YARATISH
Base.metadata.create_all(engine)


# MAHSULOT QO'SHISH
def add_product(name, price, quantity, country, image):
    with Session(engine) as session:
        product = Products(
            name=name,
            price=price,
            quantity=quantity,
            country=country,
            image=image
        )

        session.add(product)
        session.commit()


# BARCHA MAHSULOTLAR
def get_all_products():
    with Session(engine) as session:
        return session.execute(
            select(Products)
        ).scalars().all()


# BITTA MAHSULOT
def get_one_product(id):
    with Session(engine) as session:
        return session.execute(
            select(Products).where(Products.id == id)
        ).scalar()


# MAHSULOT O'CHIRISH
def delete_product(id):
    with Session(engine) as session:
        session.execute(
            delete(Products).where(Products.id == id)
        )
        session.commit()


# MAHSULOTNI YANGILASH
def edit_product_db(id, edit_content, new_content):
    with Session(engine) as session:
        session.execute(
            update(Products)
            .where(Products.id == id)
            .values(**{edit_content: new_content})
        )
        session.commit()


# SAVATGA MAHSULOT QO'SHISH
def add_order(egasi, mahsulot, miqdori, summa):
    with Session(engine) as session:

        order = session.execute(
            select(Buyurtma).where(
                Buyurtma.egasi == egasi,
                Buyurtma.mahsulot == mahsulot,
                Buyurtma.status == "cart"
            )
        ).scalar_one_or_none()

        if order:
            order.miqdori += miqdori
            order.summa += summa
        else:
            order = Buyurtma(
                egasi=egasi,
                mahsulot=mahsulot,
                miqdori=miqdori,
                summa=summa,
                status="cart"
            )
            session.add(order)

        session.commit()


# SAVATDAGI BUYURTMALAR
def buyurtmalar_olish(user_id):
    with Session(engine) as session:
        return session.execute(
            select(Buyurtma).where(
                Buyurtma.egasi == user_id,
                Buyurtma.status == "cart"
            )
        ).scalars().all()


# SAVATNI TOZALASH
def buyurtmalar_ochirish(user_id):
    with Session(engine) as session:
        session.execute(
            delete(Buyurtma).where(
                Buyurtma.egasi == user_id,
                Buyurtma.status == "cart"
            )
        )
        session.commit()


# BUYURTMANI TASDIQLASH
def confirm_order(user_id, ism, telefon, manzil):
    with Session(engine) as session:

        orders = session.execute(
            select(Buyurtma).where(
                Buyurtma.egasi == user_id,
                Buyurtma.status == "cart"
            )
        ).scalars().all()

        if not orders:
            return False

        for order in orders:
            order.status = "pending"
            order.ism = ism
            order.telefon = telefon
            order.manzil = manzil

        session.commit()
        return True


# ADMIN BUYURTMANI QABUL QILISHI
def change_orders_status(order_id):
    with Session(engine) as session:
        session.execute(
            update(Buyurtma)
            .where(
                Buyurtma.id == order_id,
                Buyurtma.status == "pending"
            )
            .values(status="accepted")
        )
        session.commit()


# ADMIN BUYURTMANI BEKOR QILISHI
def cancel_order_db(order_id):
    with Session(engine) as session:
        session.execute(
            update(Buyurtma)
            .where(
                Buyurtma.id == order_id,
                Buyurtma.status == "pending"
            )
            .values(status="cancelled")
        )
        session.commit()


# BUYURTMALAR TARIXI
def get_order_history(user_id):
    with Session(engine) as session:
        return session.execute(
            select(Buyurtma).where(
                Buyurtma.egasi == user_id,
                Buyurtma.status.in_(
                    ["pending", "accepted", "cancelled"]
                )
            ).order_by(Buyurtma.vaqt.desc())
        ).scalars().all()


# BIR BUYURTMAGA TEGISHLI MAHSULOTLAR
def get_order_products(order_id):
    with Session(engine) as session:
        return session.execute(
            select(Buyurtma).where(
                Buyurtma.id == order_id
            )
        ).scalars().all()


# ESKI ADMIN FUNKSIYASI UCHUN
def buyurtmalar_ochirish_admin(user_id):
    with Session(engine) as session:
        session.execute(
            update(Buyurtma)
            .where(
                Buyurtma.egasi == user_id,
                Buyurtma.status == "pending"
            )
            .values(status="cancelled")
        )
        session.commit()
