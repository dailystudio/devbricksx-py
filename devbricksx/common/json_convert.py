import json
import jsons

class JsonConvert(object):

    @classmethod
    def to_json(cls, obj, encoder_cls=None, pretty=False):
        if pretty:
            return json.dumps(obj, cls=encoder_cls, indent=4)
        else:
            return json.dumps(obj, cls=encoder_cls)

    @classmethod
    def to_file(cls, path, obj, encoder_cls=None, pretty=False):
        dumped_json = cls.to_json(obj, encoder_cls, pretty)
        with open(path, 'w') as json_file:
            json_file.write(dumped_json)
        return path

    @classmethod
    def from_json(cls, json_str, object_class):
        return jsons.loads(json_str, object_class)

    @classmethod
    def from_file(cls, filepath, object_class):
        result = None
        with open(filepath, 'r') as json_file:
            result = cls.from_json(json_file.read(), object_class)
        return result
