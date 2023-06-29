# def datetime_to_unix():
#     pass


# def date_parser(datetime_str):
#     custom_datetime = dtparser.parse(datetime_str).astimezone(pytz.UTC)
#     return custom_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)


# def from_remote_datetime(date_str, date_format):
#     """Parse datetime received from remote and return datetime object"""
#     if not date_str:
#         raise ValidationError(_("Please provide date"))
#     if not date_format:
#         raise ValidationError(_("Please provide date format."))
#     # not sure convert into UTC needed or not
#     try:
#         return datetime.strptime(date_str, date_format)
#     except Exception as ex:
#         raise ValidationError(_("%s") % (ustr(ex)))


# def from_iso_datetime(date_str):
#     """Parse datetime received from remote and return datetime object"""
#     date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
#     try:
#         return from_remote_datetime(date_str, date_format)
#     except Exception:
#         try:
#             date_format = "%Y-%m-%dT%H:%M:%S.%f"
#             return from_remote_datetime(date_str, date_format)
#         except Exception:
#             try:
#                 date_format = "%Y-%m-%dT%H:%M:%SZ"
#                 return from_remote_datetime(date_str, date_format)
#             except Exception:
#                 try:
#                     date_format = "%Y-%m-%d %H:%M:%S"
#                     return from_remote_datetime(date_str, date_format)
#                 except Exception:
#                     try:
#                         date_format = "%Y-%m-%dT%H:%M:%S%z"
#                         return from_remote_datetime(date_str, date_format)
#                     except Exception as ex:
#                         raise ValidationError(_("%s") % (ustr(ex)))


# def to_remote_datetime(date, date_format):
#     """Return the date in format accepted by remote"""
#     if not date:
#         raise ValidationError(_("Please provide date"))
#     if not date_format:
#         raise ValidationError(_("Please provide date format."))
#     if isinstance(date, str):
#         date = fields.Datetime.from_string(date)
#     try:
#         return date.strftime(date_format)
#     except Exception as ex:
#         raise ValidationError(_("%s") % (ustr(ex)))


# def to_iso_datetime(date):
#     """Return the date in format accepted by remote"""
#     date_format = "%Y-%m-%d %H:%M:%S"
#     try:
#         return to_remote_datetime(date, date_format)
#     except Exception as ex:
#         raise ValidationError(_("%s") % (ustr(ex)))


# def from_remote_date(date_str, date_format):
#     """Parse date received from remote and return datetime object"""
#     if not date_str:
#         raise ValidationError(_("Please provide date"))
#     if not date_format:
#         raise ValidationError(_("Please provide date format."))
#     try:
#         return datetime.strptime(date_str, date_format).date()
#     except Exception as ex:
#         raise ValidationError(_("%s") % (ustr(ex)))


# def from_iso_date(date_str):
#     """Parse date received from remote and return datetime object"""
#     date_format = "%Y-%m-%d"
#     try:
#         return from_remote_date(date_str, date_format)
#     except Exception as ex:
#         raise ValidationError(_("%s") % (ustr(ex)))


# def to_remote_date(date, date_format):
#     """Return the date in format accepted by remote"""
#     if not date:
#         raise ValidationError(_("Please provide date"))
#     if not date_format:
#         raise ValidationError(_("Please provide date format."))
#     if isinstance(date, str):
#         date = fields.Date.from_string(date)
#     try:
#         return date.strftime(date_format)
#     except Exception as ex:
#         raise ValidationError(_("%s") % (ustr(ex)))


# def check_data_type_dict(data):
#     """check the data have dictionary"""
#     if not isinstance(data, dict):
#         raise ValidationError(
#             _("Expect dictionary or json object found %s" % (type(data)))
#         )


# def formate_dict(data_dict, header=False, footer=False, line_formate=False):
#     """Prepare a string and readable representation of dictionary
#     :data_dict: data dictionary
#     :header: add at binging of result
#     :header: type: string
#     :footer: add at end of result
#     :footer: type: string
#     :line_formate: a generic format in which you want to display lines with %s
#     Ex:
#     header = <table>
#                 <thead>
#                     <tr style='font-size:16px;'>
#                         <th style='font-weight: 400;'>Attribute: </th>
#                         <th style='font-weight: 400;'>Value</th>
#                     </tr>
#                 </thead>
#                 <tbody>
#     footer = </tbody></table>
#     line_formate = <tr><th>%s: </th><th style='font-weight: 400;'>%s</th></tr>"
#     """
#     check_data_type_dict(data_dict)
#     if not data_dict:
#         return ""
#     header = header or ""
#     footer = footer or ""
#     line_formate = line_formate or "%s\t\t: %s"
#     try:
#         line_formate % ("Attribute", "Value")
#     except Exception:
#         line_formate = "%s\t\t: %s"
#     result = ""
#     dict_len = len(data_dict)
#     count = 0

#     for key, val in data_dict.items():
#         if isinstance(val, list):
#             val = ", ".join(val)
#         result += line_formate % (key, val)
#         count += 1
#         if count < dict_len:
#             result += "\n"
#     result = header + result + footer
#     return result


# def convert_tolower_case(data):
#     """convert element of list/tuple/set or keys of dictionary to lower case
#     :return: dictionary"""
#     if isinstance(data, list):
#         return [element.lower() for element in data]
#     if isinstance(data, tuple):
#         return tuple([element.lower() for element in data])
#     if isinstance(data, set):
#         return {element.lower() for element in data}
#     if isinstance(data, dict):
#         return {key.lower(): val for key, val in data.items()}
#     if isinstance(data, str):
#         return data.lower()
#     return data


# def apply_attribute_groupby(values, group_by_config, ignore_case=False):
#     """add/aggregate the attribute/values in dict as per the given configuration in
#     `group_by_config`
#     :group_by_config: Dictionary
#     format: Attribute-to-replace": {
#         "child_attributes": ["attr-1", "attr-2", "attr-3"],
#         "format": "(%s, %s, %s)",
#         "depending_attr": "attr-1",
#     }
#     :ignore_case: True/False
#     """
#     if not group_by_config:
#         return {}
#     if ignore_case:
#         values = convert_tolower_case(data=values)
#     grouped_vals = {}
#     for attribute, config in group_by_config.items():
#         attr_format = config.get("format")
#         if not config.get("child_attributes") or not attr_format:
#             continue
#         depending_attr = config.get("depending_attr")
#         depending_attr = (
#             (depending_attr and ignore_case)
#             and depending_attr.lower()
#             or depending_attr
#         )
#         if not depending_attr or depending_attr not in values:
#             continue
#         child_attr_values_lst = []
#         for child_attr in config.get("child_attributes"):
#             child_attr = ignore_case and child_attr.lower() or child_attr
#             if not values.get(child_attr):
#                 continue
#             val = values.get(child_attr)
#             if isinstance(val, list):
#                 val = ", ".join(val)
#             child_attr_values_lst.append(val)
#         try:
#             grouped_vals[attribute] = attr_format % tuple(child_attr_values_lst)
#         except Exception:
#             continue
#     return grouped_vals


# def apply_mapping(
#     values,
#     key_mapping,
#     val_mapping,
#     key_filter=None,
#     val_filter=None,
#     ignore_case=False,
#     group_by_config=None,
# ):
#     """filter and map attribute/values are per filter/mapping parameters
#     :key_mapping: dict to map keys, Ex: {key in values: key you want in final dict}
#     :key_mapping: type: dictionary
#     :val_mapping: dict to map values,
#     Ex: {value in values: value you want in final dict}
#     :val_mapping: type: dictionary
#     :key_filter: list of keys you want in final dict
#     :key_filter: type: list
#     :val_filter: list of values you want in final dict
#     :val_filter: type: list
#     :ignore_case: Boolean: marker for case-less/case-sensitive comparison
#     :range_atts: dictionary have configuration to display as combination of
#     itself or group of other attributes in specific format
#     :range_atts: type: dictionary
#     :rtype: dict
#     """
#     group_by_config = group_by_config or {}
#     # ignore case
#     if ignore_case:
#         key_mapping = convert_tolower_case(data=key_mapping)
#         val_mapping = convert_tolower_case(data=val_mapping)
#         key_filter = convert_tolower_case(data=key_filter)
#         val_filter = convert_tolower_case(data=val_filter)

#     # group/aggregate values as per configuration in `group_by_config`
#     grouped_vals = apply_attribute_groupby(
#         values=values, group_by_config=group_by_config, ignore_case=ignore_case
#     )
#     # update new vals
#     if grouped_vals:
#         values.update(grouped_vals)
#     final_values = {}
#     final_keys = {}
#     key_filter_iterable = (
#         isinstance(key_filter, list)
#         or isinstance(key_filter, tuple)
#         or isinstance(key_filter, set)
#     )
#     val_filter_iterable = (
#         isinstance(val_filter, list)
#         or isinstance(val_filter, tuple)
#         or isinstance(val_filter, set)
#     )

#     # filter attribute/values (which needs to display in product name)
#     for key, val in values.items():
#         key_com = ignore_case and key.lower() or key
#         if (key_filter or key_filter_iterable) and key_com not in key_filter:
#             continue
#         if (val_filter or val_filter_iterable) and val not in val_filter:
#             continue
#         if key_mapping:
#             key = key_mapping.get(key_com) or key
#         if val_mapping:
#             if isinstance(val, list):
#                 val = [val_mapping.get(value) or value for value in val]
#             else:
#                 val = val_mapping.get(val) or val
#         if isinstance(val, list):
#             val = ", ".join(val)
#         final_values[key_com] = val
#         final_keys[key_com] = key

#     # manage order of the attribute in name
#     order_field = key_filter or final_keys
#     return {
#         final_keys.get(key_com): final_values.get(key_com)
#         for key_com in order_field
#         if final_keys.get(key_com) and final_values.get(key_com)
#     }
