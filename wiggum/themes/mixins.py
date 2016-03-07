import logging
import os

from django.conf import settings

from applications.models import Application

SESSION_THEME_KEY = "theme"

logger = logging.getLogger(__name__)


class DynamicTemplateMixin(object):
    """ This mixin loads the tempalte based on the query param app_id. Note that
        every template hardcodes the tempalte name on the extend
    """

    DEFAULT_THEME = settings.WIGGUM_DEFAULT_THEME

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # If a template is retrieved from the app then insert app context
        app_id = self.request.GET.get("app_id", None)
        if app_id:
            app = Application.objects.get(id=app_id)
            context['app_description'] = app.description
            context['app_name'] = app.name

        return context

    def get_template_names(self):
        orig_templates = super().get_template_names()
        # First check if the template is forced
        theme = self.request.GET.get("theme", None)
        if theme:
            logger.debug("Set theme to {0}".format(theme))
            self.request.session[SESSION_THEME_KEY] = theme
            return [os.path.join(theme, i) for i in orig_templates]

        # Second check app id
        app_id = self.request.GET.get("app_id", None)
        if app_id:
            try:
                app = Application.objects.get(id=app_id)
                logger.debug("Set theme to {0}".format(app.theme))
                self.request.session[SESSION_THEME_KEY] = app.theme
                return [os.path.join(app.theme, i) for i in orig_templates]
            except Application.DoesNotExist:
                pass  # Goto default theme

        # Check if theme in session
        theme = self.request.session.get(SESSION_THEME_KEY, None)
        if theme:
            return [os.path.join(theme, i) for i in orig_templates]

        # Finally default theme
        logger.debug("Set theme to {0}".format(self.DEFAULT_THEME))
        return [os.path.join(self.DEFAULT_THEME, i) for i in orig_templates]
