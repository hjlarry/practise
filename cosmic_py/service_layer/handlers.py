from typing import Optional
from datetime import date
from dataclasses import asdict

from domain import models, commands, events
from adapters import redis_eventpublisher, notifications
from . import unit_of_work


class InvalidSku(Exception):
    pass


def add_batch(cmd: commands.CreateBatch, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        product = uow.products.get(sku=cmd.sku)
        if product is None:
            product = models.Product(cmd.sku, batches=[])
            uow.products.add(product)
        product.batches.append(models.Batch(cmd.ref, cmd.sku, cmd.qty, cmd.eta))
        uow.commit()


def allocate(cmd: commands.Allocate, uow: unit_of_work.AbstractUnitOfWork):
    line = models.OrderLine(cmd.orderid, cmd.sku, cmd.qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        product.allocate(line)
        uow.commit()


def reallocate(event: events.Deallocated, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        product = uow.products.get(sku=event.sku)
        product.events.append(commands.Allocate(**asdict(event)))
        uow.commit()


def send_out_of_stock_notification(
    event: events.OutOfStock, notifications: notifications.AbstractNotifications
):
    notifications.send(
        "stock@made.com", f"Out of stock for {event.sku}",
    )


def change_batch_quantity(
    cmd: commands.ChangeBatchQuantity, uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        product = uow.products.get_by_batchref(batchref=cmd.ref)
        product.change_batch_quantity(ref=cmd.ref, qty=cmd.qty)
        uow.commit()


def publish_allocated_event(
    event: events.Allocated, uow: unit_of_work.AbstractUnitOfWork
):
    redis_eventpublisher.publish("line_allocated", event)


def add_allocation_to_read_model(
    event: events.Allocated, uow: unit_of_work.SqlAlchemyUnitOfWork
):
    with uow:
        uow.session.execute(
            "INSERT INTO allocations_view (orderid, sku, batchref) VALUES (:orderid, :sku, :batchref)",
            dict(orderid=event.orderid, sku=event.sku, batchref=event.batchref),
        )
        uow.commit()


def remove_allocation_to_read_model(
    event: events.Deallocated, uow: unit_of_work.SqlAlchemyUnitOfWork
):
    with uow:
        uow.session.execute(
            "DELETE FROM allocations_view WHERE orderid = :orderid AND sku = :sku",
            dict(orderid=event.orderid, sku=event.sku),
        )
        uow.commit()


EVENT_HANDLERS = {
    events.OutOfStock: [send_out_of_stock_notification],
    events.Allocated: [publish_allocated_event, add_allocation_to_read_model],
    events.Deallocated: [remove_allocation_to_read_model, reallocate],
}
COMMAND_HANDLERS = {
    commands.CreateBatch: add_batch,
    commands.Allocate: allocate,
    commands.ChangeBatchQuantity: change_batch_quantity,
}
