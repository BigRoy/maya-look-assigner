from collections import defaultdict
from avalon.tools import models

from avalon.vendor.Qt import QtCore
from avalon.vendor import qtawesome
from avalon.style import colors


class AssetModel(models.TreeModel):

    Columns = ["label"]

    def add_items(self, items):
        """
        Add items to model with needed data
        Args:
            items(list): collection of item data

        Returns:
            None
        """

        self.beginResetModel()

        # Add the items sorted by label
        sorter = lambda x: x["label"]

        for item in sorted(items, key=sorter):

            asset_item = models.Item()
            asset_item.update(item)
            asset_item["icon"] = "folder"

            # Add namespace children
            namespaces = item["namespaces"]
            for namespace in sorted(namespaces):
                child = models.Item()
                child.update(item)
                child.update({
                    "label": (namespace if namespace != ":"
                              else "(no namespace)"),
                    "namespace": namespace,
                    "looks": item["looks"],
                    "icon": "folder-o"
                })
                asset_item.add_child(child)

            self.add_child(asset_item)

        self.endResetModel()

    def data(self, index, role):

        if not index.isValid():
            return

        if role == models.TreeModel.ItemRole:
            item = index.internalPointer()
            return item

        # Add icon
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                item = index.internalPointer()
                icon = item.get("icon")
                if icon:
                    return qtawesome.icon("fa.{0}".format(icon),
                                          color=colors.default)

        return super(AssetModel, self).data(index, role)


class LookModel(models.TreeModel):
    """Model displaying a list of looks and matches for assets"""

    Columns = ["label", "match"]

    def add_items(self, items):
        """Add items to model with needed data

        An item exists of:
            {
                "subset": 'name of subset',
                "asset": asset_document
            }

        Args:
            items(list): collection of item data

        Returns:
            None
        """

        self.beginResetModel()

        # Collect the assets per look name (from the items of the AssetModel)
        look_subsets = defaultdict(list)
        for asset_item in items:
            asset = asset_item["asset"]
            for look in asset_item["looks"]:
                look_subsets[look["name"]].append(asset)

        for subset, assets in sorted(look_subsets.iteritems()):

            # Define nice label without "look" prefix for readability
            label = subset if not subset.startswith("look") else subset[4:]

            item = models.Item()
            item["label"] = label
            item["subset"] = subset

            # Amount of matching assets for this look
            item["match"] = len(assets)

            # Store the assets that have this subset available
            item["assets"] = assets

            self.add_child(item)

        self.endResetModel()
