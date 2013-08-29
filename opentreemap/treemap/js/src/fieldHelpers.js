// Helper functions for fields defined by the field.html template

"use strict";

var $ = require('jquery'),
    _ = require('underscore');

exports.getField = function getField($fields, name) {
    return $fields.filter('[data-field="' + name + '"]');
};

exports.formToDictionary = function ($form, $editFields) {
    var result = {};
    _.each($form.serializeArray(), function(item) {
        var type = exports.getField($editFields, item.name).data('type');
        if (item.value === '' && (type === 'int' || type === 'float')) {
            // omit blank numbers
        } else {
            result[item.name] = item.value;
        }
    });
    return result;
};