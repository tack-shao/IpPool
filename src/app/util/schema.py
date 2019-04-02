# -*- coding: utf-8 -*-
# @Time      :2019/3/21 上午12:31
# @Author    :tack
# @Site      :
# @File      :schema.py
# @Software  :PyCharm

import functools

from werkzeug.exceptions import HTTPException

from marshmallow_peewee import ModelSchema
from marshmallow.fields import Field
from marshmallow_peewee import Related
from marshmallow.validate import (
    URL, Email, Range, Length, Equal, Regexp,
    Predicate, NoneOf, OneOf, ContainsOnly
)

URL.default_message = '无效的链接'
Email.default_message = '无效的邮箱地址'
Range.message_min = '不能小于{min}'
Range.message_max = '不能小于{max}'
Range.message_all = '不能超过{min}和{max}这个范围'
Length.message_min = '长度不得小于{min}位'
Length.message_max = '长度不得大于{max}位'
Length.message_all = '长度不能超过{min}和{max}这个范围'
Length.message_equal = '长度必须等于{equal}位'
Equal.default_message = '必须等于{other}'
Regexp.default_message = '非法输入'
Predicate.default_message = '非法输入'
NoneOf.default_message = '非法输入'
OneOf.default_message = '无效的选择'
ContainsOnly.default_message = '一个或多个无效的选择'
Field.default_error_messages = {
        'required': '该字段是必填字段',
        'type': '无效的输入类型',
        'null': '字段不能为空',
        'validator_failed': '无效的值'
}


def validate_schema(_model, **schema_kwargs):

    """
    用于检查参数正确性。

    :param _model: 数据库模块，用于绑定字段校验。
    :param schema_kwargs:  根据marshmallow.schema.Schema的
                            参数要求进行要求，下面是详细参数列表:
                            extra=None
                            only=()
                            exclude=()
                            prefix=''
                            strict=None
                            many=False
                            context=None
                            load_only=()
                            dump_only=()
                            partial=False
    :return: 校验正确则执行handler，校验失败则返回错误信息。
    """

    def decorator(f):
        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):

            class CommonSchema(ModelSchema):

                class Meta:
                    model = _model

            # 检查验证结果
            result, errors = (CommonSchema(**schema_kwargs)
                              .load(self.plain_arguments()))

            # 当验证结果存在错误时, 返回错误信息.
            if errors:
                msg = ['{}{}'.format(getattr(_model, k).verbose_name, v[0])
                       for k, v in errors.items()]
                raise HTTPException(status_code=400, log_message='\n'.join(msg))

            # 当验证结果正确时, 执行handler.
            return f(self, *args, **kwargs)
        return wrapper
    return decorator


def serializer_schema(_model, *related, **schema_kwargs):
    """
    用于序列化。
    :param _model: 数据库模块，用于绑定字段校验。
    :param related: 声明那些关联字段是需要一起序列化的，参数格式如下:
                     [
                     # 表示外键
                     (field_name, None),
                     # 表示该字段为不是关联字段，但序列化需要存在的字段.
                     (field_name, callback)
                     ]
    :param schema_kwargs: 根据marshmallow.schema.Schema的
                            参数要求进行要求，下面是详细参数列表:
                            extra=None
                            only=()
                            exclude=()
                            prefix=''
                            strict=None
                            many=False
                            context=None
                            load_only=()
                            dump_only=()
                            partial=False
    :return: 返回经过序列化后的数据集。
    """

    class CommonSchema:
        class Meta:
            model = None

    # 绑定类对象
    CommonSchema.Meta.model = _model
    [setattr(CommonSchema, field, callback())
     if callback else setattr(CommonSchema, field, Related())
     for field, callback in related]

    # 混入
    schema_cls = type(
        str('CommonSchema'), (CommonSchema, ModelSchema), {}
    )

    return schema_cls(**schema_kwargs)
