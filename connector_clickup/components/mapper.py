from odoo.addons.component.core import AbstractComponent


class ClickupImportMapper(AbstractComponent):
    _name = "clickup.import.mapper"
    _inherit = ["base.clickup.connector", "base.import.mapper"]
    _usage = "import.mapper"


class ClickupExportMapper(AbstractComponent):
    _name = "clickup.export.mapper"
    _inherit = ["base.clickup.connector", "base.export.mapper"]
    _usage = "export.mapper"


class ClickupImportMapperChild(AbstractComponent):
    """:py:class:`MapChild` for the Imports"""

    _name = "clickup.map.child.import"
    _inherit = ["base.clickup.connector", "base.map.child.import"]
    _usage = "import.map.child"

    def skip_item(self, map_record):
        print("MAP CHILD RECORD=", map_record)
        record = map_record.source
        if not record["attributes"]["quantity"]:
            return True

    def get_item_values(self, map_record, to_attr, options):
        print("MAP CHILD RECORD=", map_record)
        values = map_record.values(**options)
        binder = self.binder_for()
        binding = binder.to_internal(map_record.source["id"])
        if binding:
            # already exists, keeps the id
            values["id"] = binding.id
        return values

    def format_items(self, items_values):
        print("MAP CHILD RECORD=")
        # if we already have an ID (found in get_item_values())
        # we change the command to update the existing record
        items = []
        for item in items_values[:]:
            if item.get("id"):
                binding_id = item.pop("id")
                # update the record
                items.append((1, binding_id, item))
            else:
                # create the record
                items.append((0, 0, item))
        return items


# class SaleLineMapChild(Component):
#     _name = 'foo.sale.line.import.map.child'
#     _inherit = ['foo.connector', 'base.map.child.import']
#     _apply_on = 'foo.sale.order.line'

#     def skip_item(self, map_record):
#         record = map_record.source
#         if not record['attributes']['quantity']:
#             return True

#     def get_item_values(self, map_record, to_attr, options):
#         values = map_record.values(**options)
#         binder = self.binder_for()
#         binding = binder.to_internal(map_record.source['id'])
#         if binding:
#             # already exists, keeps the id
#             values['id'] = binding.id
#         return values

#     def format_items(self, items_values):
#         # if we already have an ID (found in get_item_values())
#         # we change the command to update the existing record
#         items = []
#         for item in items_values[:]:
#             if item.get('id'):
#                 binding_id = item.pop('id')
#                 # update the record
#                 items.append((1, binding_id, item))
#             else:
#                 # create the record
#                 items.append((0, 0, item))
#         return items
