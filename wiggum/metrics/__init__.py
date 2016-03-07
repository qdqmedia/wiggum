
from prometheus_client import Counter

# Prometheus metrics
failed_logins_total = Counter('failed_logins_total',
                              'Failed logins',
                              labelnames=['app_name', ])

succeeded_logins_total = Counter('succeeded_logins_total',
                                 'Succeeded logins',
                                 labelnames=['app_name', ])

password_reset_requests_total = Counter('password_reset_requests_total',
                                        'Password reset requests',
                                        labelnames=['app_name', ])

password_resets_total = Counter('password_resets_total',
                                'Password resets',
                                labelnames=['app_name', ])

impersonations_total = Counter('impersonations_total',
                               'Impersonations',
                               labelnames=['app_name', ])


logouts_total = Counter('logouts_total',
                               'Logouts',
                               labelnames=['app_name', ])


def _add_constant_context(context):
    context['app_name'] = "wiggum"
    return context


def inc_failed_login(context={}):
    context = _add_constant_context(context)
    failed_logins_total.labels(context).inc()


def inc_succeeded_login(context={}):
    context = _add_constant_context(context)
    succeeded_logins_total.labels(context).inc()


def inc_password_reset_requests(context={}):
    context = _add_constant_context(context)
    password_reset_requests_total.labels(context).inc()


def inc_password_resets(context={}):
    context = _add_constant_context(context)
    password_resets_total.labels(context).inc()


def inc_impersonations(context={}):
    context = _add_constant_context(context)
    impersonations_total.labels(context).inc()


def inc_logouts(context={}):
    context = _add_constant_context(context)
    logouts_total.labels(context).inc()
